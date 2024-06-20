import os
import uuid
import logging
from multiprocessing import Process
from bs4 import BeautifulSoup
from datetime import datetime

from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from webdriver_manager.chrome import ChromeDriverManager


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

SCREENSHOT_DIR = os.getenv('SCREENSHOT_DIR', 'file_path/screenshots')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
Base = declarative_base()


class Screenshot(Base):
    __tablename__ = 'screenshots'
    id = Column(String, primary_key=True)
    path = Column(String)
    run_id = Column(String)


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()


def get_browser_with_service():
    chrome_service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=chrome_service)

def fix_links_without_https_prefix(links, start_url):
    for link in links:
        if not link.startswith('http'):
            yield start_url + link
        else:
            yield link

def get_screenshots_with_links(browser, links, run_id):
    screenshots = []
    for link_index, link in enumerate(links):
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'{run_id}_link_{link_index}.png')
        browser.get(link)
        browser.save_screenshot(screenshot_path)
        screenshot = Screenshot(id=str(uuid.uuid4()), path=screenshot_path, run_id=run_id)
        screenshots.append(screenshot)

    return screenshots

def save_screenshots_and_links(screenshots):
    session = Session()
    try:
        session.add_all(screenshots)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logging.error(f"Error saving screenshots: {str(e)}")
        return False
    finally:
        session.close()


def crawl_website(start_url, num_links, run_id):
    screenshot_path = os.path.join(SCREENSHOT_DIR, f'{run_id}_start.png')
    try:
        with get_browser_with_service() as browser:
            browser.get(start_url)
            browser.save_screenshot(screenshot_path)

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True)][:num_links]

            prefixed_links = list(fix_links_without_https_prefix(links, start_url))
            screenshots = get_screenshots_with_links(browser, prefixed_links, run_id)
            if save_screenshots_and_links(screenshots):
                logging.info(f"Successfully saved screenshots and links for run_id {run_id}")
            else:
                logging.error(f"Failed to save screenshots and links for run_id {run_id}")

    except Exception as e:
        logging.error(f"Error during crawling for run_id {run_id}: {str(e)}")


@app.route('/isalive', methods=['GET'])
def is_alive():
    return jsonify(status="alive"), 200


@app.route('/screenshot', methods=['GET'])
def take_screenshot():
    with get_browser_with_service() as browser:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f'screenshot_{timestamp}.png')
        browser.save_screenshot(screenshot_path)

    logging.info(f"Screenshot saved to {screenshot_path}")
    return jsonify(status="success", path=screenshot_path), 200


@app.route('/screenshots', methods=['POST'])
def start_crawling():
    data = request.get_json()
    start_url = data.get('start_url')
    num_links = data.get('num_links')

    if not start_url or not isinstance(num_links, int):
        return jsonify(status="error", message="Invalid parameters"), 400

    run_id = str(uuid.uuid4())
    process = Process(target=crawl_website, args=(start_url, num_links, run_id))
    process.start()

    return jsonify(status="success", run_id=run_id), 200


@app.route('/screenshots/<run_id>', methods=['GET'])
def get_screenshots(run_id):
    session = Session()
    screenshots = session.query(Screenshot).filter_by(run_id=run_id).all()

    if not screenshots:
        return jsonify(status="error", message="No screenshots found for the given ID"), 404

    screenshot_paths = [screenshot.path for screenshot in screenshots]
    return jsonify(status="success", screenshots=screenshot_paths), 200


if __name__ == '__main__':
    db_url = 'sqlite:///screenshots.db'
    db = Database(db_url)
    app.run(host='0.0.0.0', port=5001)