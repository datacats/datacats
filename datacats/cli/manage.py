from ConfigParser import SafeConfigParser

from datacats.project import Project, ProjectError

def stop(opts):
    try:
        project = Project.load(opts['PROJECT'])
    except ProjectError as e:
        print e
        return

    project.stop_web()
    project.stop_data_and_search()
