from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_spiders():
    """运行所有爬虫"""
    logger.info("开始运行爬虫抓取价格数据...")
    try:
        # 运行京东爬虫
        result = subprocess.run(
            ['scrapy', 'crawl', 'jd'],
            cwd='f:/Files/GitHub Files/film-price-tracker',
            capture_output=True,
            text=True
        )
        logger.info(f"京东爬虫运行结果: {result.returncode}")
        if result.stdout:
            logger.info(f"标准输出: {result.stdout}")
        if result.stderr:
            logger.warning(f"标准错误: {result.stderr}")
        
        # 可以添加其他平台的爬虫
        # subprocess.run(['scrapy', 'crawl', 'taobao'], ...)
        # subprocess.run(['scrapy', 'crawl', 'amazon'], ...)
        
        logger.info("爬虫运行完成")
    except Exception as e:
        logger.error(f"运行爬虫时出错: {e}")

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = BackgroundScheduler()
    
    # 每天凌晨2点运行爬虫
    scheduler.add_job(
        run_spiders,
        trigger=CronTrigger(hour=2, minute=0),
        id='run_spiders_daily',
        name='每天运行爬虫抓取价格数据',
        replace_existing=True
    )
    
    # 也可以添加其他时间的任务
    # 例如每6小时运行一次
    # scheduler.add_job(
    #     run_spiders,
    #     trigger=CronTrigger(hour='*/6'),
    #     id='run_spiders_every_6_hours',
    #     name='每6小时运行爬虫抓取价格数据',
    #     replace_existing=True
    # )
    
    scheduler.start()
    logger.info("定时任务调度器已启动")
    
    return scheduler

if __name__ == '__main__':
    scheduler = start_scheduler()
    
    # 保持程序运行
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
