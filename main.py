import re
from datetime import datetime, timedelta
from shotgun_api3 import Shotgun
import getpass
import socket


class active_time:

    def __init__(self, paths):
        """
        initializing patters nd formats and variables
        :param paths:path is a list containing paths of a log file
        """
        self.save_proj = re.compile(r'(.*?) (.*?) (.*?) (.*?) Saving Project \'(.*?)\'.*?')
        self.save_workspace = re.compile(r'(.*?) (.*?) (.*?) (.*?) Saving workspace \'Workspace \((.*?)\)\'.')
        self.load_proj = re.compile(r'(.*?) (.*?) (.*?) (.*?) Loaded Project \'(.*?)\' @.*?')
        self.date_format = "%m/%d/%y:%H:%M:%S.%f"
        self.proj_det = {}
        self.time_data = {}
        self.__sg_connection()
        for path in paths:
            try:
                self.__loads_saves(path)
            except OSError as e:
                print('No File Found')
        self.__calculate_time()

    def __sg_connection(self):
        """
        Make a sg connection
        :return:
        """
        self.sg = Shotgun(
            base_url="https://samit.shotgunstudio.com",
            # password
        )

    def __loads_saves(self, path):
        """
        reads from the log files and capture the required details by string matching
        :param path: path to the log file
        :return:
        """
        with open(path, "r") as log:
            for line in log:
                match_save = self.save_proj.match(line)
                match_save_wrk = self.save_workspace.match(line)
                match_load = self.load_proj.match(line)

                if match_load:

                    time = datetime.strptime(match_load.group(4), self.date_format)
                    project = match_load.group(5)
                    type = "load"

                elif match_save_wrk:

                    time = datetime.strptime(match_save_wrk.group(4), self.date_format)
                    project = match_save_wrk.group(5)
                    type = "save"

                elif match_save:

                    time = datetime.strptime(match_save.group(4), self.date_format)
                    project = match_save.group(5)
                    type = 'save'

                if match_load or match_save or match_save_wrk:
                    if project in self.proj_det:
                        self.proj_det[project].append([type, time])
                    else:
                        self.proj_det[project] = [[type, time]]

    def __calculate_time(self):
        """
        calculate the time spent based on the details found from the log file (loading and saving time)
        :return:
        """
        for proj in self.proj_det:
            time_var = timedelta(0, 0, 0, 0)
            #print(i)
            start = 0
            for log in self.proj_det[proj]:
                #print(logs)
                if log[0] == 'load':
                    start = log[1]

                elif log[0] == 'save':
                    cur_time = log[1] - start
                    time_var = time_var + cur_time
                    start = log[1]

                self.date = log[1]
            self.time_data[proj] = time_var

    def add_to_sg(self):
        """
        public function to start with adding projects to sg
        :return:
        """
        for i in self.time_data:
            user = getpass.getuser
            if self.time_data[i] != timedelta(0, 0, 0, 0):
                self.__sg_add(i, self.time_data[i])

    def display_details(self):
        for i in self.time_data:
            if self.time_data[i] != timedelta(0, 0, 0, 0):
                print(i, self.time_data[i])

    def __sg_add(self, project, time, user_id=881):
        """
        find and add the details to sg page
        :param project: name of the project (str)
        :param time: time spent of the project (timedelta)
        :param user_id: the id of the user for the log file (int)
        :return:
        """
        print(project, time)
        entity_type = "CustomNonProjectEntity04"
        entity_id = 1

        # schema = self.sg.schema_field_read(entity_type)
        # for i in schema:
        #     print(i)

        user = self.sg.find_one('HumanUser', [['id', 'is', user_id]], [])
        time = time.total_seconds()/3600
        host_ip = self.__get_ip()
        date = self.date.date()

        data = {
            'sg_user': user,
            'sg_date': date,
            'sg_project': project,
            'sg_time_spent__hours_': time,
            'sg_host_ip': host_ip
        }
        print(data)
        new_row = self.sg.create(entity_type, data)

    def __get_ip(self):
        """
        Find the IP adress of the current system
        :return: the ip adress
        """
        hostname = socket.gethostname()
        address = socket.gethostbyname(hostname)
        return address


if __name__ == '__main__':

    logs_paths = ["C:/Users/s8/OneDrive - Autodesk/Desktop/Logs/flame20233_flame2_app.log", "C:/Users/s8/OneDrive - Autodesk/Desktop/Logs/flame20233_flame1_app.log.1"]
    sg = active_time(logs_paths)
    sg.display_details()
    #sg.add_to_sg()



