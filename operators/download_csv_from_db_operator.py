"""
Operador que executa uma query SQL, gera um arquivo CSV com o resultado
e grava o arquivo no sistema de arquivo.

Args:
    mssql_conn_id (str): Airflow conn_id do BD onde a query select_sql
    será executada
    select_sql (str): query que retorna os dados que serão gravados no
    CSV
    target_file_dir (str): local no sistema de arquivo onde o arquivo
    CSV será gravado
    file_name (str): nome para o arquivo CSV a ser gravado
    int_columns (str): lista com nome das colunas que são do tipo
    inteiro para geração correta do arquivo CSV
"""

import os

from airflow.operators.bash_operator import BaseOperator
from airflow.hooks.mssql_hook import MsSqlHook
from airflow.utils.decorators import apply_defaults


class DownloadCSVFromDbOperator(BaseOperator):
    ui_color = '#95aad5'
    ui_fgcolor = '#000000'
    template_fields = ('select_sql', 'target_file_dir', 'file_name')

    @apply_defaults
    def __init__(self,
                 mssql_conn_id,
                 select_sql,
                 target_file_dir,
                 file_name,
                 int_columns=None,
                 *args,
                 **kwargs
                 ):
        super(DownloadCSVFromDbOperator, self).__init__(*args, **kwargs)
        self.mssql_conn_id = mssql_conn_id
        self.select_sql = select_sql
        self.int_columns = int_columns
        self.target_file_dir = target_file_dir
        self.file_name = file_name

    def execute(self, context):
        mssql_hook = MsSqlHook(mssql_conn_id=self.mssql_conn_id)
        df = mssql_hook.get_pandas_df(self.select_sql)

        # Convert columns data types to int
        if self.int_columns:
            for col in self.int_columns:
                df[col] = df[col].astype("Int64")

        # Create folder if not exists
        if not os.path.exists(self.target_file_dir):
            os.mkdir(self.target_file_dir)

        file_path = os.path.join(self.target_file_dir, self.file_name)
        df.to_csv(file_path, index=False)
