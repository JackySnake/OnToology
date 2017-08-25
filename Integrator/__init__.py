import ConfigParser
import os
import random
import string
from subprocess import call

import logging


ontology_formats = ['.rdf', '.owl', '.ttl']
config_folder_name = 'OnToology'
config_file_name = 'OnToology.cfg'
log_file_dir = ''  # need to be set some how
# verification_log_fname = 'verification.log'

g = None

# def dolog(msg):
#     print(msg)
#     # dolog_function(msg)

tools_conf = {
    'ar2dtool': {'folder_name': 'diagrams', 'type': 'png'},
    'widoco': {'folder_name': 'documentation'},
    'oops': {'folder_name': 'evaluation'},
    'owl2jsonld': {'folder_name': 'context'}
}


def dolog_logg(msg):
    logging.critical(msg)


def p(msg):
    print(msg)

dolog = p


def prepare_logger(log_fname):
    logging.basicConfig(filename=log_fname, format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)


def tools_execution(changed_files, base_dir, logfile, dolog_fname=None, target_repo=None, g_local=None,
                    change_status=None, repo=None):
    """
    :param changed_files:  changed files include relative path
            base_dir: abs dir to the repo file name, e.g. /home/user/myrepo/
    :return:
    """
    global g
    global dolog
    global log_file_dir
    g = g_local
    log_file_dir = logfile
    if dolog_fname is not None:
        prepare_logger(dolog_fname)
        dolog = dolog_logg
    repo.notes = ''
    repo.save()
    progress_out_of = 70.0
    if len(changed_files) == 0:
        repo.progress = progress_out_of
        repo.save()
        return
    single_piece = progress_out_of/len(changed_files)
    progress_inc = single_piece/4.0
    for f in changed_files:
        if f[-4:] in ontology_formats:
            if f[:len('OnToology/')] == 'OnToology/':  # This is to solve bug #265
                dolog("nested prevented bug: "+f)
                continue
            dolog("tools_execution: "+f)
            handle_single_ofile(f, base_dir, target_repo=target_repo, change_status=change_status, repo=repo,
                                progress_inc=progress_inc)


def handle_single_ofile(changed_file, base_dir, target_repo, change_status, repo=None, progress_inc=0.0):
    """
    assuming the change_file is an ontology file
    :param changed_file: relative directory of the file e.g. dir1/dir2/my.owl
    :param base_dir:
    :param target_repo:
    :param change_status:
    :param repo: a Repo instance of the target repo
    :param progress_inc: how much to increment the progress after each
    :return:
    """
    import ar2dtool
    import widoco
    import oops
    import owl2jsonld
    import syntaxchecker
    dolog("will call create or get conf")
    conf = create_of_get_conf(changed_file, base_dir)
    dolog("conf: "+str(conf))
    if not syntaxchecker.valid_syntax(os.path.join(base_dir, changed_file)):
        repo.notes += "syntax error in %s\n" % changed_file
        repo.save()
        return
    if conf['ar2dtool_enable']:
        dolog("will call draw diagrams")
        change_status(target_repo, 'drawing diagrams for: '+changed_file)
        r = ar2dtool.draw_diagrams([changed_file], base_dir)
        if r != "":
            print 'in init draw detected an error'
            # repo.notes += 'Error generating diagrams for %s. ' % changed_file
            repo.save()
    repo.progress += progress_inc
    repo.save()
    if conf['widoco_enable']:
        dolog('will call widoco')
        change_status(target_repo, 'generating docs for: '+changed_file)
        r = widoco.generate_widoco_docs([changed_file], base_dir)
        if r != "":
            print 'in init documentation detected an error for ontology file: %s' % changed_file
            # repo.notes += 'Error generating documentation for %s. ' % changed_file
            repo.save()
    repo.progress += progress_inc
    repo.save()
    if conf['oops_enable']:
        dolog('will call oops')
        change_status(target_repo, 'evaluating: '+changed_file)
        r = oops.oops_ont_files(target_repo=target_repo, changed_files=[changed_file], base_dir=base_dir)
        if r != "":
            print 'in init evaluation detected an error'
            # repo.notes += 'Error generating evaluation for %s. ' % changed_file
            repo.save()
    repo.progress += progress_inc
    repo.save()
    if conf['owl2jsonld_enable']:
        dolog('will call owl2jsonld')
        change_status(target_repo, 'generating context for: '+changed_file)
        owl2jsonld.generate_owl2jsonld_file([changed_file], base_dir=base_dir)
    repo.progress += progress_inc
    repo.save()


def create_of_get_conf(ofile, base_dir):
    """
    :param ofile: relative directory of the file e.g. dir1/dir2/my.owl
    :return:
    """
    ofile_config_file_rel = os.path.join(config_folder_name, ofile, config_file_name)
    ofile_config_file_abs = os.path.join(base_dir, ofile_config_file_rel)
    build_path(ofile_config_file_abs)
    dolog('config is called')
    ar2dtool_sec_name = 'ar2dtool'
    widoco_sec_name = 'widoco'
    oops_sec_name = 'oops'
    owl2jsonld_sec_name = 'owl2jsonld'
    ar2dtool_enable = True
    widoco_enable = True
    oops_enable = True
    owl2jsonld_enable = True
    config = ConfigParser.RawConfigParser()
    conf_file = config.read(ofile_config_file_abs)
    config_file_needs_rewrite = False  # becuase there were a missing key or section
    config_values = {
        ar2dtool_sec_name: {
            "enable": True
        },
        widoco_sec_name: {
            "enable": True
        },
        oops_sec_name: {
            "enable": True
        },
        owl2jsonld_sec_name: {
            "enable": True
        }
    }
    if len(conf_file) == 1:
        dolog(ofile+' configuration file exists')
        for section in config_values.keys():
            try:
                config.add_section(section)
                config_file_needs_rewrite = True
            except:
                pass
            for k in config_values[section].keys():
                try:
                    config_values[section][k] = config.getboolean(section, k)
                    dolog('got %s %s value: %s' % (section, k, config_values[section][k]))
                except:
                    config_file_needs_rewrite = True
                    config.set(section, k, config_values[section][k])
                    dolog('not found %s %s' % (section, k))

        # try:
        #     ar2dtool_enable = config.getboolean(ar2dtool_sec_name, 'enable')
        #     dolog('got ar2dtool enable value: ' + str(ar2dtool_enable))
        # except:
        #     dolog('ar2dtool enable value doesnot exist')
        #     ar2dtool_enable = False
        #     config.set(ar2dtool_sec_name, 'enable', ar2dtool_enable)
        #     pass
        # try:
        #     widoco_enable = config.getboolean(widoco_sec_name, 'enable')
        #     dolog('got widoco enable value: ' + str(widoco_enable))
        # except:
        #     dolog('widoco enable value doesnot exist')
        #     widoco_enable = False
        #     config.set(widoco_sec_name, 'enable', ar2dtool_enable)
        #     pass
        # try:
        #     oops_enable = config.getboolean(oops_sec_name, 'enable')
        #     dolog('got oops enable value: ' + str(oops_enable))
        # except:
        #     dolog('oops enable value doesnot exist')
        #     oops_enable = False
        # try:
        #     owl2jsonld_enable = config.getboolean(owl2jsonld_sec_name, 'enable')
        #     dolog('got owl2jsonld enable value: ' + str(owl2jsonld_enable))
        # except:
        #     dolog('owl2jsonld enable value doesnot exist')
        #     owl2jsonld_enable = False
    else:
        dolog(ofile+' configuration file does not exists (not an error)')
        dolog('full path is: '+ofile_config_file_abs)
        config_file_needs_rewrite = True
        for section in config_values.keys():
            try:
                config.add_section(section)
            except:
                pass
            for k in config_values[section].keys():
                config.set(section, k, config_values[section][k])




        # config.add_section(ar2dtool_sec_name)
        # config.set(ar2dtool_sec_name, 'enable', ar2dtool_enable)
        # config.add_section(widoco_sec_name)
        # config.set(widoco_sec_name, 'enable', widoco_enable)
        # config.add_section(oops_sec_name)
        # config.set(oops_sec_name, 'enable', oops_enable)
        # config.add_section(owl2jsonld_sec_name)
        # config.set(owl2jsonld_sec_name, 'enable', owl2jsonld_enable)
        # dolog('will create conf file: ' + ofile_config_file_abs)
        # try:
        #     with open(ofile_config_file_abs, 'wb') as configfile:
        #         config.write(configfile)
        # except Exception as e:
        #     dolog('exception: ')
        #     dolog(e)
    if config_file_needs_rewrite:
        try:
            with open(ofile_config_file_abs, 'wb') as configfile:
                config.write(configfile)
        except Exception as e:
            dolog('exception: ')
            dolog(e)

    return config_values
    # return {'ar2dtool_enable': ar2dtool_enable,
    #         'widoco_enable': widoco_enable,
    #         'oops_enable': oops_enable,
    #         'owl2jsonld_enable': owl2jsonld_enable}


#######################
# helper functions  ###
#######################

def build_path(file_with_abs_dir):
    """
    :param file_with_abs_dir:
    :return: abs_dir as string
    """
    # file_with_abs_dir = os.path.join(repo_abs_dir, file_with_rel_dir)
    abs_dir = get_parent_path(file_with_abs_dir)
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)
    dolog("build_path abs_dir: "+abs_dir)  # file_with_abs_dir
    return file_with_abs_dir


def delete_dir(target_directory):
    comm = "rm -Rf " + target_directory
    comm += '  >> "' + log_file_dir + '" '
    dolog(comm)
    call(comm, shell=True)


def get_parent_path(f):
    return '/'.join(f.split('/')[0:-1])


def get_file_from_path(f):
    return f.split('/')[-1]


def get_target_home():
    return 'OnToology'


def call_and_get_log(comm):
    """
    :param comm: The command to be executed via call
    :return: error message, output of the call
    """
    temp_dir = os.environ['github_repos_dir']
    sec = ''.join([random.choice(string.ascii_letters + string.digits)
                   for _ in range(9)])
    fname_output = 'call-output-'+sec
    fname_output = os.path.join(temp_dir, fname_output)
    fname_err = 'call-error-'+sec
    fname_err = os.path.join(temp_dir, fname_err)
    f = open(fname_output, 'w')
    ferr = open(fname_err, 'w')
    call(comm, stdout=f, stderr=ferr, shell=True)
    f.close()
    ferr.close()
    f = open(fname_output, 'r')
    ferr = open(fname_err, 'r')
    file_content = f.read()
    error_content = ferr.read()
    f.close()
    ferr.close()
    os.remove(fname_output)
    os.remove(fname_err)
    return error_content, file_content

timeout_comm = "timeout 300;"
error_msg, output_msg = call_and_get_log(timeout_comm+" echo 'testing timeout command'")
if error_msg.strip() != "":
    timeout_comm = "gtimeout 300;" # for mac os
    error_msg, output_msg = call_and_get_log(timeout_comm+" echo 'testing gtimeout command'")
    if error_msg.strip() != "": # incase timeout and gtimeout are not installed
        timeout_comm = "echo "

# disable the timeout for now
timeout_comm = ""