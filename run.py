#---运行----

from core.Scheduler import Scheduler

def main():
    try:
        s = Scheduler()
        s.run()
    except:
        main()


if __name__ == '__main__':
    main()