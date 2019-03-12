import os
import sys
import subprocess
import stat
import shutil
import time
from ROOT import TStopwatch, PyConfig, gROOT
PyConfig.IgnoreCommandLineOptions = True
gROOT.SetBatch(True)

class batchConfig(object):
    """
    base class for submitting jobs to a batch system.
    The options for different hosts are specified in the object 'hostoptionsdict_':
    hostoptionsdict_ = {
        "hostkeyword": {
            "init_message" : "Message to be displayed when initializing the batchConfig object",
            "option_1" : "VALUE",
            "option_2" : "VALUE",
            ...
        }
    }
    When a batchConfig object is initialized, the class checks whether 'hostkeyword' is part of the hostname.
    If it is not specified, the default is used (currently HTCondor as used on DESY NAF). 
    You can add options for a host using the function 'addhost'.

    Current list of options that can be set:
    queue       --  queue that is to be used (on old lxplus batch)
    subname     --  name of the command used to submit jobs (e.g. 'qsub' for SGE, 'condor_submit' for HTCondor)
    arraysubmit --  boolean which indicates whether the submission of multiple jobs as array is supported or not
    subopts     --  list of additional options for subitting jobs 
                    (only do this if you want to reset the default submit options, else use 'addoption', 'setoption', 'removeoption')
    jobmode     --  name of system used to submit jobs (HTCondor -> 'HTC', DESY naf birds -> 'SGE', old lxplus batch -> "lxbatch")
    """
    hostname_ = "NOTSET"
    queue_ = "NOTSET"
    subname_ = "NOTSET"
    arraysubmit_ = False
    subopts_ = []
    jobmode_ = "NOTSET"

    subopts_ = ["universe = vanilla"]
    subopts_.append("should_transfer_files = IF_NEEDED")
    subopts_.append("notification = Never")
    subopts_.append("priority = 0")
    subopts_.append("run_as_owner = true")
    subopts_.append("max_retries = 3")
    subopts_.append("retry_until = ExitCode == 0")
    # subopts_.append("RequestMemory = 2500")
    # subopts_.append("+RequestRuntime = 86400")
    # subopts_.append("RequestDisk = 2000000")

    # print temp_
    # print temp_.split("\n")
    hostoptionsdict_ = {
        "nafhh-cms" : {
            "init_message" : "detected DESY naf bird system",
            "jobmode" : "SGE",
            "subname" : "qsub",
            "subopts" : "-l h=bird* -hard -l os=sld6 -l h_vmem=2000M -l s_vmem=2000M -cwd -S /bin/bash -V".split(),
            "arraysubmit" : True,
        },
        "lxplus" : {
            "init_message" : "Using lxplus HTCondor system!",
            "jobmode" : "lxplus_HTC",
            "subname" : "condor_submit",
            "arraysubmit" : True,
        },
        "default" : {
            "init_message" : "Using default: HTCondor system!",
            "jobmode" : "HTC",
            "subname" : "condor_submit",
            "arraysubmit" : True,
        }
    }
    # print hostoptionsdict_["default"]["subopts"]
    def __init__(self, hostname="", queue = ""):
        if not hostname:
            a = subprocess.Popen(["hostname"], stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
            output = a.communicate()[0]
            output.replace('\n',"")
            self.hostname_ = output
        else:
            self.hostname_ = hostname

        host = "default"
        for key in self.hostoptionsdict_:
            if key in self.hostname_:
                host = key

        optionsdict = self.hostoptionsdict_[host]
        print optionsdict["init_message"]
        if "queue" in optionsdict:
            self.queue_ = optionsdict["queue"]
        if "subname" in optionsdict:
            self.subname_ = optionsdict["subname"]
        if "arraysubmit" in optionsdict:
            self.arraysubmit_ = optionsdict["arraysubmit"]
        if "jobmode" in optionsdict:
            self.jobmode_ = optionsdict["jobmode"]
        if "subopts" in optionsdict:
            self.subopts_ = optionsdict["subopts"]

    def addhost(self, hostkeyword, dictionary):
        """
        Add options a new host. The variable 'hostkeyword' has to be part of the hostname.

        Current list of options that can be set:
        queue       --  queue that is to be used (on old lxplus batch)
        subname     --  name of the command used to submit jobs (e.g. 'qsub' for SGE, 'condor_submit' for HTCondor)
        arraysubmit --  boolean which indicates whether the submission of multiple jobs as array is supported or not
        subopts     --  list of additional options for subitting jobs
        jobmode     --  name of system used to submit jobs (HTCondor -> 'HTC', DESY naf birds -> 'SGE', old lxplus batch -> "lxbatch")
        memory      --  amount of memory to be requested in MB, e.g. "2000M" (currently only on HTCondor)
        diskspace   --  diskspace to be requested in byte (currently only on HTCondor)
        runtime     --  runtime to be requested in seconds (currently only on HTCondor)
        """
        if not (hostkeyword == "" or len(dictionary)==0):
            self.hostoptionsdict_[hostkeyword] = dictionary

    def addoption(self, optionsstring):
        """
        Add options for the current host.
        """
        self.subopts_.append(optionsstring)

    def removeoption(self, attribute):
        if attribute == "diskspace":
            attribute = "RequestDisk"
        elif attribute == "runtime":
            attribute = "+RequestRunTime"
        elif attribute == "memory":
            attribute = "RequestMemory"
        index = self.get_index_for_attribute(attribute)
        if index != None:
            self.subopts_.pop(index)
        else:
            print "Attribute does not exist for this batchConfig, will do nothing"

    def get_index_for_attribute(self, attribute):
        """
        Check if there is a line in 'subopts_' that starts with 'attribute'.
        Return index if possible, otherwise None 
        """
        index = None

        for x in self.subopts_:
            temp = x.split()
            if len(temp) == 0: continue
            if temp[0] == attribute:
                index = self.subopts_.index(x)
                break
        return index


    def setoption(self, attribute, optionsstring):
        """
        Check if a line in 'subopts_' starts with 'attribute' and change this entry to 'optionsstring'.
        If 'attribute' is not in 'subopts_', return False
        """
        index = self.get_index_for_attribute(attribute = attribute)
        s = " = ".join([attribute, optionsstring])
        print "setting '%s' for submit" % s
        if index != None:
            self.subopts_[index] = s
        else:
            self.addoption(optionsstring = s)


    @property
    def hostname(self):
        """return hostname """
        return self.hostname_

    @hostname.setter
    def hostname(self, name):
        """setter for hostname """
        self.hostname_ = name

    @property
    def memory(self):
        """
        Return value for 'RequestMemory' keyword in 'subopts' if it's available
        """
        index = self.get_index_for_attribute("RequestMemory")
        return self.subopts_[index].split(" = ")[-1]
    @memory.setter
    def memory(self, value):
        """
        First check if 'value' can be a float. Then call 'self.setoption' with the attribute 'RequestMemory'
        """
        test = None
        if isinstance(value, float) or isinstance(value, int):
            test = str(value)
        elif isinstance(value, str):
            if value.isnumeric(): test = value
        else:
            print "Input value is not a number, could not set memory!"

        if not test == None:
            self.setoption(attribute = "RequestMemory", optionsstring = str(value))

    @property
    def diskspace(self):
        """
        Return value for 'RequestDisk' keyword in 'subopts' if it's available
        """
        index = self.get_index_for_attribute("RequestDisk")
        return self.subopts_[index].split(" = ")[-1]
    @diskspace.setter
    def diskspace(self, value):
        """
        First check if 'value' can be a float. Then call 'self.setoption' with the attribute 'RequestDisk'
        """
        test = None
        if isinstance(value, float) or isinstance(value, int):
            test = str(value)
        elif isinstance(value, str):
            if value.isnumeric(): test = value
        else:
            print "Input value is not a number, could not set diskspace!"
        if test != None:
            self.setoption(attribute = "RequestDisk", optionsstring = str(value))

    @property
    def runtime(self):
        """
        Return value for '+RequestRuntime' keyword in 'subopts' if it's available
        """
        index = self.get_index_for_attribute("+RequestRuntime")
        return self.subopts_[index].split(" = ")[-1]
    @runtime.setter
    def runtime(self, value):
        """
        First check if 'value' can be a float. Then call 'self.setoption' with the attribute '+RequestRuntime'
        """
        test = None
        if isinstance(value, float) or isinstance(value, int):
            test = str(value)
        elif isinstance(value, str):
            value = unicode(value, "utf-8")
            if value.isnumeric(): test = value
        else:
            print "Input value is not a number, could not set runtime!"

        if not test == None:
            self.setoption(attribute = "+RequestRuntime", optionsstring = str(value))
    def __str__(self):
        """overload print(batchConfig_base) here"""
        slist = ["options for this batchConfig:"]
        slist += ["\thostname_ = " +self.hostname_]
        slist += ["\tqueue_ = "+self.queue_]
        slist += ["\tsubname_ = "+ self.subname_]
        slist += ["\tarraysubmit_ = " + str(self.arraysubmit_)]
        slist += ["\tsubopts_ = [\n" + "\t,\n".join(self.subopts_) + "]"]
        slist += ["\tmemory_ = "+ self.memory_]
        slist += ["\tjobmode_ = " + self.jobmode_]
        return "\n".join(slist)

    def writeSubmitCode(self, script, logdir, hold = False, isArray = False, nscripts = 0):
        '''
        write the code for condor_submit file
        script: path to .sh-script that should be executed
        logdir: path to directory of logs
        hold: boolean, if True initates the sript in hold mode, can be released manually or inbuild submitXXXtoBatch functions
        isArray: set True if script is an array script
        nscripts: number of scripts in the array script. Only needed if isArray=True
        
        returns path to generated condor_submit file
        '''
        submitPath = script.replace(".sh",".sub")
        submitScript = ".".join(os.path.basename(script).split(".")[:-1])
        
        submitCode = ""
        if len(self.subopts_) != 0:
            submitCode = "\n".join(self.subopts_)
            submitCode += "\n"
        if self.jobmode_ == "lxplus_HTC":
            submitCode+="executable = " + script + "\n"
            submitCode+="arguments = $(SGE_TASK_ID)\n"
        else:
            submitCode +="executable = /bin/bash\n"
            submitCode+="arguments = " + script + "\n"
        submitCode+="initialdir = "+os.getcwd()+"\n"

        if hold:
            submitCode+="hold = True\n"

        if isArray:
            submitCode+="error = "+logdir+"/"+submitScript+".$(Cluster)_$(ProcId).err\n"
            submitCode+="output = "+logdir+"/"+submitScript+".$(Cluster)_$(ProcId).out\n"
            submitCode+="log = "+logdir+"/"+submitScript+".$(Cluster)_$(ProcId).log\n"
            submitCode+="Queue Environment From (\n"
            for taskID in range(nscripts):
                submitCode+="\"SGE_TASK_ID="+str(taskID)+"\"\n"
            submitCode+=")"
        else:
            submitCode+="error = "+logdir+"/"+submitScript+".$(Cluster).err\n"
            submitCode+="output = "+logdir+"/"+submitScript+".$(Cluster).out\n"
            submitCode+="log = "+logdir+"/"+submitScript+".$(Cluster).log\n"
            submitCode+="queue"

        submitFile = open(submitPath, "w")
        submitFile.write(submitCode)
        submitFile.close()
        return submitPath


    def writeArrayCode(self, scripts, arrayPath):
        '''
        write code for array script
        scripts: scripts to be executed by array script
        arrayPath: filename of array script

        returns arrayPath (redundand but safer than no return)
        '''
        arrayCode="#!/bin/bash \n"
        arrayCode+="subtasklist=("
        for scr in scripts:
            arrayCode+=scr+" \n"

        arrayCode+=")\n"
        if "HTC" in self.jobmode_:
            arrayCode+="thescript=${subtasklist[$SGE_TASK_ID]}\n"
            arrayCode+="echo \"${thescript}\"\n"
            arrayCode+=". $thescript"
        else:
            arrayCode+="thescript=${subtasklist[$SGE_TASK_ID-1]}\n"
            arrayCode+="thescriptbasename=`basename ${subtasklist[$SGE_TASK_ID-1]}`\n"
            arrayCode+="echo \"${thescript}\n"
            arrayCode+="echo \"${thescriptbasename}\n"
            arrayCode+=". $thescript 1>>"+logdir+"/$JOB_ID.$SGE_TASK_ID.o 2>>"+logdir+"/$JOB_ID.$SGE_TASK_ID.e\n"
        arrayFile=open(arrayPath,"w")
        arrayFile.write(arrayCode)
        arrayFile.close()
        st = os.stat(arrayPath)
        os.chmod(arrayPath, st.st_mode | stat.S_IEXEC)
        return arrayPath

    def construct_array_submit(self):
        command = None
        command = [self.subname_, '-terse','-o', '/dev/null', '-e', '/dev/null']
        command += self.subopts_
        return command
    
    def setupRelease(self, oldJIDs, newJID):
        filepath = os.path.abspath(os.path.realpath(__file__))
        basedir = os.path.dirname(filepath)
        fname = os.path.basename(filepath)
        module = ".".join(fname.split(".")[:-1])
        releaseCode = "import sys\n"
        releaseCode += 'basedir = "' + basedir + '"\n'
        releaseCode += "if not basedir in sys.path:\n"
        releaseCode += "\tsys.path.append(basedir)\n"
        releaseCode += "from " + module +" import *\n"
        releaseCode += "import os\n"
        releaseCode += "q = " + module + "()\n"
        releaseCode += "q.do_qstat("+str(oldJIDs)+")\n"
        releaseCode += "os.system('condor_release "+str(newJID)+"')"
        
        releasePath = "release_"+str(newJID)+".py"
        print(releasePath)
        with open(releasePath, "w") as releaseFile:
            releaseFile.write(releaseCode)
        os.system("python "+releasePath+" > /dev/null && rm "+releasePath+" &")
        #time.sleep(5)
        #os.system("rm "+releasePath)

    def submitArrayToBatch(self, scripts, arrayscriptpath, jobid = None):
        '''
        submits given scripts as array to batch system
        scripts: scripts to be submitted as array
        arrayscriptpath: path to generated array file
        jobid: newly created array job waits for the jobs given in jobid (as a list of ids) before executing

        returns jobid of array as list
        '''
        submitclock=TStopwatch()
        submitclock.Start()
        arrayscriptpath = os.path.abspath(arrayscriptpath)

        logdir = os.path.dirname(arrayscriptpath)+"/logs"
        print "will save logs in", logdir
        # if os.path.exists(logdir):
        #     print "emptying directory", logdir
        #     shutil.rmtree(logdir)
        # os.makedirs(logdir)
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        
        # write array script
        nscripts=len(scripts)
        tasknumberstring='1-'+str(nscripts)

        arrayscriptpath = self.writeArrayCode(scripts, arrayscriptpath)
        
        # prepate submit
        if "HTC" in self.jobmode_:
            print 'writing code for condor_submit-script'
            hold = True if jobid else False
            submitPath = self.writeSubmitCode(arrayscriptpath, logdir, hold = hold, isArray = True, nscripts = nscripts)
            
            print 'submitting',submitPath
            command = self.subname_ + " -terse " + submitPath
            command = command.split()
        else:
            print 'submitting',arrayscriptpath
            command = self.construct_array_submit()
            if not command:            
                print "could not generate array submit command"
                return 
            command.append('-t')
            command.append(tasknumberstring)
            if jobid:
                command.append("-hold_jid")
                command.append(str(jobid))
            command.append(arrayscriptpath)
        
        # submitting
        print "command:", command
        a = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
        output = a.communicate()[0]
        jobidstring = output
        if len(jobidstring)<2:
            sys.exit("something did not work with submitting the array job")
        
        # extracting jobid
        try:
            jobidint = int(output.split(".")[0])
        except:
            sys.exit("something went wrong with calling condor_submit command, submission of jobs was not succesfull")
        submittime=submitclock.RealTime()
        print "submitted job", jobidint, " in ", submittime
        if hold:
            self.setupRelease(jobid, jobidint)
        return [jobidint]
    
    def submitJobToBatch(self, script, jobid = None):
        '''
        submits a single job to batch system
        script: script to be submitted
        jobid: new job  waits for the jobs given in jobid (as a list of ids) before executing

        returns jobid of submitted job as list
        '''
        script = os.path.abspath(script)
        st = os.stat(script)
        dirname = os.path.dirname(script)
        os.chmod(script, st.st_mode | stat.S_IEXEC)
        cmdlist = [self.subname_]
        logdir = os.path.join(dirname, "logs")
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        if self.jobmode_ == "HTC":
            hold = True if jobid else False
            submitPath = self.writeSubmitCode(script, logdir, hold = hold)
            cmdlist.append("-terse")
            cmdlist.append(submitPath)
        else:
            cmdlist += self.subopts_
            temp = "-o {0}/log.out -e {0}/log.err".format(logdir)
            cmdlist += temp.split()
            if jobid:
                cmdlist.append("-hold_jid")
                cmdlist.append(str(jobid))
            cmdlist.append(script)
        jobids = []
        #command = " ".join(cmdlist)
        print "command:", cmdlist
        a = subprocess.Popen(cmdlist, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
        output = a.communicate()[0]
        #print output
        if self.jobmode_ == "HTC":
            try:
                jobidint = int(output.split(".")[0])
            except:
                sys.exit("something went wrong with calling condor_submit command, submission of jobs was not succesfull")
        else:
            jobidstring = output.split()
            for jid in jobidstring:
                if jid.isdigit():
                    jobidint=int(jid)
                    continue

        print "this job's ID is", jobidint
        jobids.append(jobidint)
        if hold:
            self.setupRelease(jobid, jobidint)
        return jobids
        
    def do_qstat(self, jobids):
        '''
        monitoring of job status
        jobids: which jobs to be monitored

        returns nothing, only stops if no more jobs are running/idling/held
        '''
        allfinished=False
        while not allfinished:
            time.sleep(10)
            statname = ['condor_q'] if self.jobmode_ == "HTC" else ['qstat']
            if self.jobmode_ == "HTC":
                statname += jobids
                statname = [str(stat) for stat in statname]
            a = subprocess.Popen(statname, stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
            qstat=a.communicate()[0]
            lines=qstat.split('\n')
            nrunning=0
            if self.jobmode_ == "HTC":
                for line in lines:
                    if "Total for query" in line:
                        joblist = line.split(";")[1]
                        states = joblist.split(",")
                        jobs_running = int(states[3].split()[0])
                        jobs_idle =  int(states[2].split()[0])
                        jobs_held = int(states[4].split()[0])
                        nrunning = jobs_running + jobs_idle + jobs_held
            else:
                for line in lines:
                    words=line.split()
                    for jid in words:
                        if jid.isdigit():
                            jobid=int(jid)
                            if jobid in jobids:
                                nrunning+=1
                                break
    
            if nrunning>0:
                print nrunning,'jobs running'
            else:
                allfinished=True
    
