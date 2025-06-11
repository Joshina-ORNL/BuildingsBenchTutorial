import argparse
try:
    import pyspark
except:
    print('please install pyspark with `pip install pyspark`')
    exit(1)

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import TimestampNTZType
import os
import glob

conf = SparkConf().setMaster("local[*]").setAppName("pytorch2")
conf.set("spark.executor.memory", "2g")
conf.set("spark.driver.memory", "64G")
conf.set("spark.executor.cores", "96")
conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
conf.set("spark.default.parallelism", "96")
conf.set("spark.local.dir", "/tmp/scratch/tmp2")
sc =  SparkContext.getOrCreate(conf=conf)
spark = SparkSession(sc)
# Set the environment variable SPARK_LOCAL_DIRS
os.environ['SPARK_LOCAL_DIRS'] = '/tmp/scratch/tmp2'


def main(args):

    eulp_dir = os.path.join(args.eulp_dir, 'end-use-load-profiles-for-us-building-stock', '2021')
    output_dir = args.output_dir

    census_regions = ['by_puma_midwest', 'by_puma_northeast', 'by_puma_south', 'by_puma_west'] 
    years = ['amy2018', 'tmy3']
    
    for cr in census_regions:

        for year in years:

            for res_or_com in ['resstock', 'comstock']:
                
                list_of_pumas = glob.glob(os.path.join(eulp_dir,
                                                       f'{res_or_com}_{year}_release_1',
                                                       'timeseries_individual_buildings',
                                                       cr,
                                                       'upgrade=0',
                                                       'puma=*'))
                target_path = os.path.join(output_dir, 'end-use-load-profiles-for-us-building-stock' , '2021',
                                            f'{res_or_com}_{year}_release_1',
                                            'timeseries_individual_buildings',
                                            cr,
                                            'upgrade=0')
                
                for puma_id in list_of_pumas:
                    print(f'processing {puma_id} to store buildings as a parquet file...')

                    target_puma_path = os.path.join(target_path, os.path.basename(puma_id))
                    if not os.path.isdir(target_puma_path):
                        os.makedirs(target_puma_path)
                    else:
                        print(f'{target_puma_path} already exists. Skipping...')
                        continue
                    
                    # reads every individual building timeseries in a single puma
                    df = spark.read.parquet(puma_id).select(['`out.site_energy.total.energy_consumption`', 'timestamp', 'bldg_id'])
                    # electricity only
                    #df = spark.read.parquet(puma_id).select(['`out.electricity.total.energy_consumption`', 'timestamp', 'bldg_id'])

                    # Sum 15 min out.site_energy.total.energy_consumption by hour for each bldg_id
                    df = df.withColumn('timestamp', df.timestamp - F.expr('INTERVAL 15 minutes'))
                    df = df.withColumn('timestamp', F.date_trunc('hour', df['timestamp']).cast(TimestampNTZType()))

                    df = df.groupBy('timestamp', 'bldg_id').agg(F.sum('`out.site_energy.total.energy_consumption`').alias('total_energy_consumption'))
                    #df = df.groupBy('timestamp', 'bldg_id').agg(F.sum('`out.electricity.total.energy_consumption`').alias('total_energy_consumption'))

                    # Group by timestamp and create a new column for each bldg_id
                    df = df.groupBy('timestamp').pivot('bldg_id').agg(F.first('total_energy_consumption'))
                    # fill na with 0
                    df = df.fillna(0)

                    df = df.repartition(1)
                    # Save as dataset with parquet files
                    df.write.option('header', True).mode('overwrite').parquet(target_puma_path)


if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument('--eulp_dir', type=str, required=True,
                        help='Path to raw EULP data.')
    args.add_argument('--output_dir', type=str, required=True,
                        help='Path to store the processed data.')
    
    args = args.parse_args()

    main(args)
