from ConfigParser import SafeConfigParser

from datacats.project import Project, ProjectError

def stop(project):
    project.stop_web()
    project.stop_data_and_search()

def start(project):
    ip = project.web_ipaddress()
    if ip is not None:
        print 'Already running at http://{0}/'.format(ip)
        return
    project.start_data_and_search()
    project.start_web()
    ip = project.web_ipaddress()
    print 'Now available at http://{0}/'.format(ip)
