from ConfigParser import SafeConfigParser

from datacats.project import Project, ProjectError

def stop(project):
    project.stop_web()
    project.stop_data_and_search()

def start(project):
    address = project.web_address()
    if address is not None:
        print 'Already running at {0}'.format(address)
        return
    project.start_data_and_search()
    project.start_web()
    print 'Now available at {0}'.format(project.web_address())
