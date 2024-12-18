import asyncio
import os
import zipfile
import tempfile
import pandas as pd
import requests
from io import BytesIO
from playwright.async_api import async_playwright

if not os.path.exists('klines'):
    os.makedirs('klines')

async def download_klines():
    prefix = "data/spot/monthly/klines/BTCUSDT/1m/"
    url = f"https://data.binance.vision/?prefix={prefix}"
    download_url = f"https://data.binance.vision/{prefix}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector('#listing:has-text(".zip")')

        zip_files = await page.locator('//a[contains(@href, ".zip")]').all_inner_texts()
        zip_files = filter(lambda x: not x.endswith('CHECKSUM'), zip_files)

        downloaded_files = get_already_downloaded_files()
        zip_files = list(map(lambda x: x.replace('.zip', ''), zip_files))
        zip_files = list(set(zip_files) - set(downloaded_files))
        zip_files.sort()

        for zip_file in zip_files:
            print(f"Downloading {zip_file}")
            with tempfile.TemporaryDirectory() as tmpdirname:
                zip_path = os.path.join(tmpdirname, f"{zip_file}.zip")
                response = requests.get(f"{download_url}{zip_file}.zip")
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                process_zipfile(zip_path)

        await browser.close()

def get_already_downloaded_files():
    return list(map(lambda x: x.replace('.csv', ''), os.listdir('./klines')))

def process_zipfile(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        name = zip_ref.namelist()[0]
        data = zip_ref.read(name)
        names = [
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ]
        df = pd.read_csv(BytesIO(data), names=names)
        columns_to_save = ['open_time', 'open', 'high', 'low', 'close']
        df[columns_to_save].to_csv(f'klines/{name}', index=False, lineterminator='\n')
        return name

if __name__ == "__main__":
    asyncio.run(download_klines())
