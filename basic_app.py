__author__ = 'dsilva2014'


import json
import logging
import logging.handlers
from error.error_manager import ErrorManager
from progress.progress_manager import ProgressManager
from documents.document_manager import DocumentManager


class BasicApp(object):

    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.main_configuration = self.get_configuration()
        self.application_name = self.init_application_name()
        self.logger = self.init_logger()
        self.progress_manager = self.init_progress_manager()
        self.error_manager = ErrorManager()
        try:
            self.document_manager = self.init_document_manager()
        except Exception as e:
            self.logger.critical(e)


    def init_application_name(self):
        main_configuration = self.main_configuration
        application_configuration = main_configuration["application_configuration"]
        application_name = application_configuration["application_name"]
        return application_name

    def init_progress_manager(self):
        progress_manager = ProgressManager(self.logger)
        progress_manager.activate()
        return progress_manager

    def get_configuration(self):
        json_data = open(self.configuration_filename)
        data = json.load(json_data)
        return data

    def get_application_name(self):
        return self.application_name

    def init_logger(self):
        main_configuration = self.main_configuration
        logger_configuration = main_configuration["logger_configuration"]
        format = logger_configuration["format"]
        logging.basicConfig(format=format)
        logger = logging.getLogger(self.get_application_name())
        logger.setLevel(logging.DEBUG)
        """
        smtp_handler = self.get_smtp_handler()
        logger.addHandler(smtp_handler)
        """
        file_handler = self.get_file_handler()
        logger.addHandler(file_handler)
        return logger

    def init_document_manager(self):
        database_configuration = self.main_configuration["database_configuration"]
        document_manager = DocumentManager(database_configuration)
        return document_manager

    def get_file_handler(self):
        file_handler = None
        if file_handler is None:
            try:
                file_handler = logging.FileHandler("logs/"+self.get_application_name() + ".log")
            except:
                pass
        if file_handler is None:
            try:
                file_handler = logging.FileHandler("../logs/"+self.get_application_name() + ".log")
            except:
                pass
        file_handler.setLevel(logging.DEBUG)
        return file_handler

    def get_smtp_handler(self):
        main_configuration = self.main_configuration
        smtp_handler_configuration = main_configuration["smtp_handler_configuration"]
        mailhost = smtp_handler_configuration["mailhost"]
        fromaddr = smtp_handler_configuration["fromaddr"]
        toaddrs = smtp_handler_configuration["toaddrs"]
        subject = self.application_name + ' : ' + smtp_handler_configuration["subject"]
        user = smtp_handler_configuration["user"]
        pwd = smtp_handler_configuration["pwd"]
        smtp_handler = logging.handlers.SMTPHandler(mailhost=mailhost,
                                                    fromaddr=fromaddr,
                                                    toaddrs=toaddrs,
                                                    subject=subject,
                                                    credentials=(user, pwd),
                                                    secure=())
        smtp_handler.setLevel(logging.INFO)
        return smtp_handler

    def step(self):
        self.progress_manager.step()

    def process(self):
        pass

    def start(self):
        self.logger.info("App started: " + self.get_application_name())
        try:
            self.process()
        except IOError as e:
            self.error_manager.add(e.strerror)
        except Exception as e:
            self.error_manager.add(e)
        self.logger.info("App finished: " + self.get_application_name())
        if self.error_manager.is_errors_exist():
            errors = self.error_manager.errors.exceptions
            self.logger.critical(str(len(errors)) + " error(s)!")
            for error in errors:
                self.logger.critical("Error: " + str(error))