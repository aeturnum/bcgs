from server import app


#bind = "unix:bcgs.sock"
#workers = 2
#reload = True

application = app

if __name__ == '__main__':
    app.run()
