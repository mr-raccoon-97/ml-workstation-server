import sys, os, logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
logging.basicConfig(level=logging.INFO, format='%(levelname)s:     %(message)s')

if __name__ == '__main__':
    from uvicorn import run
    from messagebus.api import api
    run(api, host='0.0.0.0', port=8001, log_level='info')