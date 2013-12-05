def build_config(settings):
    return _find_project_jenkins_job_names(settings)


def _find_project_jenkins_job_names(settings):
    """Parse the INI settings for the list of GH project and Jenkins jobs

    The pattern is that they come in \n separated. They're expected to be in
    matched order.

    """
    jenkins = settings.get('jenkins.merge.job')
    github = settings.get('github.project')

    if not jenkins or not github:
        raise ValueError('The settings must include a Jenkins job and a '
                         'Github project to monitor.')

    jenkins_list = jenkins.split('\n')
    github_list = github.split('\n')

    if len(jenkins_list) != len(github_list):
        raise ValueError('The number of jenkins jobs and github projects do'
                         'not match')

    # Add a new 'projects' key to the settings that is indexed on the github
    # project list.
    settings['projects'] = {}
    for i, proj in enumerate(github_list):
        settings['projects'][proj] = jenkins_list[i]

    return settings
