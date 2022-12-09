
from . import tasks

def main_soup():
    try:
        tasks.start_yahoo_scraper()

    except Exception as e:
        print(f"an error occured {e}")



if __name__ == '__main__':
    print('will run')
    main_soup()