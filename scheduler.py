from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import logging
import threading
from config import config

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app_config = config['default']


def run_spiders():
    logger.info("开始运行爬虫抓取价格数据...")
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'taobao'],
            cwd=app_config.SCRAPER_CWD,
            capture_output=True,
            text=True
        )
        logger.info(f"淘宝爬虫运行结果: {result.returncode}")
        if result.stdout:
            logger.info(f"标准输出: {result.stdout}")
        if result.stderr:
            logger.warning(f"标准错误: {result.stderr}")

        logger.info("爬虫运行完成")
    except Exception as e:
        logger.error(f"运行爬虫时出错: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_spiders,
        trigger=CronTrigger(hour=2, minute=0),
        id='run_spiders_daily',
        name='每天运行爬虫抓取价格数据',
        replace_existing=True
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")

    return scheduler


if __name__ == '__main__':
    scheduler = start_scheduler()
    shutdown_event = threading.Event()

    try:
        shutdown_event.wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
