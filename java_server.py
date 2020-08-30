import sys
from py4j.clientserver import ClientServer, JavaParameters, PythonParameters
from py4j.java_collections import JavaList, ListConverter
from py4j.java_gateway import JavaGateway


class JavaServer(object):

    def run(self, package, class_name=None, method_name=None, parm1=None, parm2=None):
        # todo import var name package
        print(sys.path)
        import main
        package_name = package
        try:
            import package_name
        except:
            print(None)

    def shutdown(self):
        client_server.close()

    def say_hello(self, int_value=None, string_value=None):
        print(int_value, string_value)
        return self._covert_list([int_value, string_value])

    def audio_time(self, file):
        from main_speech_recognize import SpeechRecognize
        recognize = SpeechRecognize(file)
        clips = recognize.get_time_clips()
        return self._covert_list(clips)

    def _covert_list(self, py_list: list):
        """
        covert py list to java list contain list in list
        :param py_list: py list
        :return: java list
        """
        gateway = JavaGateway()
        if type(py_list[0]) is list:
            java_list = ListConverter().convert([], gateway._gateway_client)
            for l in py_list:
                j_l = ListConverter().convert(l, gateway._gateway_client)
                java_list.append(j_l)
        else:
            java_list = ListConverter().convert(py_list, gateway._gateway_client)
        return java_list

    def java_list_oppend(self,List):
        pass

    class Java:
        implements = ["com.alan.Client"]


if __name__ == '__main__':
    client_server = ClientServer(
        java_parameters=JavaParameters(),
        python_parameters=PythonParameters(),
        python_server_entry_point=JavaServer())
    print("Server started")