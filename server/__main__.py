import sys, os, logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    from uvicorn import run
    from server.api import api
    run(api, host='0.0.0.0', port=8000)