import logging
import logging.config
import logging.handlers as handlers
import os
import threading 
import sys
from logging.handlers import TimedRotatingFileHandler

from typing import List, Dict, Tuple, Set, Optional
import pathlib
from boxing.utils import Utils
from boxing.logger import BoxingLogger
import os.path
import pandas as pd
from datetime import datetime as dt






class Metrics():
    """Represents the class with auxiliary functions for logs written by the library.
    """

    def __init__(
            self,
            map_id: str,
            execution_time: float,
            memory_objects_beginning: int,
            memory_objects_end: int,
            memory_use: float,
            res_dir: str,
            filepath: str,
            verbose: bool
        ) -> None:
        """Initializes the metrics class.
        """
        self._map_id = map_id
        self._verbose = verbose
        self._box_log_utils = BoxingLogger(map_id = map_id, name = 'metric_log', verbose = self.verbose)
        self._logger = self._box_log_utils.logger
        self._execution_time = execution_time
        self._memory_objects_beginning = memory_objects_beginning
        self._memory_objects_end = memory_objects_end
        self._memory_use = memory_use
        self._filename = '\\metrics.csv'
        self._res_dir = res_dir
        self._filepath = filepath

        self.log_metrics()
        self.save_metrics()
        
        
    @property
    def verbose(self) -> bool:
        """Gets the verbose option.
        """
        return self._verbose
    @property
    def map_id(self) -> str:
        """Gets the map identifier.
        """
        return self._map_id

    @property
    def logger(self) -> logging:
        """Gets the logging object.
        """
        return self._logger

    @property
    def box_log_utils(self) -> BoxingLogger:
        """Gets the BoxingLogger object .
        """
        return self._box_log_utils
    @property
    def execution_time(self) -> float:
        """Gets the algorithm execution time .
        """
        return self._execution_time
    @property
    def memory_objects_beginning(self) -> int:
        """Gets the quantity of objects in memory at the beginning 
           of the algorithm.
        """
        return self._memory_objects_beginning
    @property
    def memory_objects_end(self) -> int:
        """Gets the quantity of objects in memory at the end
           of the algorithm.
        """
        return self._memory_objects_end 

    @property
    def filename(self) -> str:
        """Gets the metrics' filename.
        """
        return self._filename
    @property
    def memory_use(self) -> float:
        """Gets the memory use.
        """
        return self._memory_use
    @property
    def res_dir(self) -> str:
        """Returns results folder
        """
        return self._res_dir
    @property
    def filepath(self) -> str:
        """Returns filepath
        """
        return self._filepath

    def format_dataframe(self, df_metrics):
        df_metrics = df_metrics.drop(df_metrics.tail(3).index)
        df_metrics.idx = df_metrics.idx.apply(lambda x: str(x))
        df_metrics.map = df_metrics.map_id.apply(lambda x: str(x))
        df_metrics.execution_time_seconds = df_metrics.execution_time_seconds.apply(lambda x: float(x))
        df_metrics.memory_use_gb = df_metrics.memory_use_gb.apply(lambda x: float(x))
        df_metrics.memory_objects_beginning = df_metrics.memory_objects_beginning.apply(lambda x: tuple(map(float, x[1:-1].split(', '))))
        df_metrics.memory_objects_end = df_metrics.memory_objects_end.apply(lambda x: tuple(map(float, x[1:-1].split(', '))))
        df_metrics.qt_warnings = df_metrics.qt_warnings.apply(lambda x: float(x))
        return df_metrics

    def get_colname(self, beg):
        if beg:
            col_name = 'memory_objects_beginning'
        else:
            col_name = 'memory_objects_end'
        return col_name
    
    def get_avg_objects_memory(self, df, beginning = True):

        col_name = self.get_colname(beg = beginning)
        res = []
        len_tp = 3
        len_df = len(df)
        for i in range(len_tp):
            lists = [df[col_name].iloc[j][i] for j in range(len_df)]
            res.append(sum(lists)/len(df))

        return tuple(res)
    def get_min_objects_memory(self, df, beginning = True):

        col_name = self.get_colname(beg = beginning)
        res = []
        len_tp = 3
        len_df = len(df)
        for i in range(len_tp):
            lists = [df[col_name].iloc[j][i] for j in range(len_df)]
            res.append(min(lists))

        return tuple(res)
    def get_max_objects_memory(self, df, beginning = True):

        col_name = self.get_colname(beg = beginning)
        res = []
        len_tp = 3
        len_df = len(df)
        for i in range(len_tp):
            lists = [df[col_name].iloc[j][i] for j in range(len_df)]
            res.append(max(lists))
        return tuple(res)

    def log_metrics(self):
        exec_time = "{:.2f}".format(round(self.execution_time, 2))
        mem_use = "{:.2f}".format(round(self.memory_use, 2))
        self.logger.debug(f"Metrics: execution time = {exec_time} seconds, memory use = {mem_use}, objects in memory at the beginning: {self.memory_objects_beginning}, objects in memory at the end: {self.memory_objects_end}")

    def save_metrics(self):
        full_filename = self.filepath + self.res_dir + '\\metrics.csv'
        file_exists = os.path.exists(full_filename)
        sample_index = dt.now().strftime("%m/%d/%Y, %H:%M:%S")

        if file_exists:
            metrics_df = self.format_dataframe(df_metrics = pd.read_csv(full_filename, dtype={'map_id': str}))
            
            
        else:
            metrics_df = pd.DataFrame()

        new_row = {'idx':str(sample_index), 
                   'map_id':str(self.map_id), 
                   'execution_time_seconds':self.execution_time, 
                   'memory_use_gb': self.memory_use,
                   'memory_objects_beginning':self.memory_objects_beginning, 
                   'memory_objects_end':self.memory_objects_end}
       
        
        metrics_df = metrics_df.append(new_row, ignore_index = True)
        metrics_df_new = metrics_df.mean()
        new_row = {'idx':'avg', 
                       'map_id':0, 
                       'execution_time_seconds':metrics_df_new.execution_time_seconds, 
                       'memory_use_gb': metrics_df_new.memory_use_gb,
                       'memory_objects_beginning': self.get_avg_objects_memory(df = metrics_df, beginning = True), 
                       'memory_objects_end': self.get_avg_objects_memory(df = metrics_df, beginning = False)}
        metrics_df = metrics_df.append(new_row, ignore_index = True)
        metrics_df_new = metrics_df.max()
        new_row = {'idx':'max', 
                       'map_id':0, 
                       'execution_time_seconds':metrics_df_new.execution_time_seconds, 
                       'memory_use_gb': metrics_df_new.memory_use_gb,
                       'memory_objects_beginning':self.get_max_objects_memory(df = metrics_df, beginning = True), 
                       'memory_objects_end':self.get_max_objects_memory(df = metrics_df, beginning = False)}
        metrics_df = metrics_df.append(new_row, ignore_index = True)
        metrics_df_new = metrics_df.min()
        new_row = {'idx':'min', 
                       'map_id':0, 
                       'execution_time_seconds':metrics_df_new.execution_time_seconds, 
                       'memory_use_gb': metrics_df_new.memory_use_gb,
                       'memory_objects_beginning':self.get_min_objects_memory(df = metrics_df, beginning = True), 
                       'memory_objects_end':self.get_min_objects_memory(df = metrics_df, beginning = False)}
        metrics_df = metrics_df.append(new_row, ignore_index = True)
        metrics_df = metrics_df.set_index('idx')
        metrics_df.to_csv(full_filename)



       
    




    
   

    
