from datetime import datetime
import time as t
import psutil as p
from mysql.connector import connection

# CPU: Uso da cpu:  p.cpu_percent; IoWait: cpu_times 
# DISCO: Uso do disco; Iops; 
# MEMÓRIA RAM: Uso da memória ram; Swap da ram; 

db = connection.MySQLConnection(
    host="localhost",
    port=3306,
    user="root",
    passwd="", # falta add a senha do bd aqui
    database="lowLatency"
)

cursor = db.cursor()
print("""\n
---------------------------------------------------------------------------                                                                      

 █                    █               █                               
 █                    █               █                               
 █       ███  █░    █ █      ░███░  █████   ███   █▒██▒   ▓██▒  █░  █ 
 █      █▓ ▓█ ▓▒   ▒█ █      █▒ ▒█    █    ▓▓ ▒█  █▓ ▒█  ▓█  ▓  ▓▒ ▒▓ 
 █      █   █ ░█ █ █▒ █          █    █    █   █  █   █  █░     ▒█ █▒ 
 █      █   █  █▒█▒█  █      ▒████    █    █████  █   █  █       █ █  
 █      █   █  █████  █      █▒  █    █    █      █   █  █░      █▓▓  
 █      █▓ ▓█  ▒█▒█▒  █      █░ ▓█    █░   ▓▓  █  █   █  ▓█  ▓   ▓█▒  
 ██████  ███    █ █   ██████ ▒██▒█    ▒██   ███▒  █   █   ▓██▒   ▒█   
                                                                 ▒█   
                                                                 █▒   
                                                                ██    
--------------------------------------------------------------------------
Software de captura versão: 2.0
Data da última versão: 14-10-2026
--------------------------------------------------------------------------
\n""")

def menuCaptura(fk_servidor):


    iops_t1 = p.disk_io_counters()
    tempo_t1 = t.time()

    while True:

            try:
                iops_t2 = p.disk_io_counters()
                tempo_t2 = t.time()

                delta_tempo = tempo_t2 - tempo_t1
                if delta_tempo > 0 and iops_t1 and iops_t2:
                    ops_leitura = iops_t2.read_count - iops_t1.read_count
                    ops_escrita = iops_t2.write_count - iops_t1.write_count
                    iops_total = (ops_leitura + ops_escrita) / delta_tempo
                else:
                    iops_total = 0

                agora = datetime.now()
                data_formatada = agora.strftime("%d/%m/%Y")
                hora_atual = agora.strftime("%H:%M:%S")

                print("Data e Hora da Captura: ")
                print(data_formatada, hora_atual, '\n')

                for i in range(1, 8):

                    valor = 0.0
                    fk_unidade_medida = i
                    alerta = 0
                    fk_metrica = 0
                    fk_componente = 0
                    
                    if i == 1:
                        valor = p.cpu_percent(interval=1)
                        fk_metrica = 1
                        fk_componente = 1
                        
                        if valor > 70:
                            alerta = 1

                    elif i == 2:
                        valor = p.cpu_times_percent().softirq
                        fk_metrica = 2
                        fk_componente = 1
                        
                        if valor > 5:
                            alerta = 1

                    elif i == 3:
                        valor = getattr(p.cpu_times, 'iowait', 0.0)
                        fk_metrica = 3
                        fk_componente = 1
                        
                        if valor > 0.1:
                            alerta = 1

                    elif i == 4:
                       valor = p.virtual_memory().percent
                       fk_metrica = 4
                       fk_componente = 2
                       
                       if valor > 65:
                            alerta = 1

                    elif i == 5:
                        valor = p.swap_memory().percent
                        fk_metrica = 5
                        fk_componente = 2
                        
                        if valor > 0:
                            alerta = 1

                    elif i == 6:
                        valor = p.disk_usage('/').percent
                        fk_metrica = 6
                        fk_componente = 3
                        
                        if valor > 65:
                            alerta = 1
                    
                    elif i == 7:
                        valor = iops_total
                        fk_metrica = 7
                        fk_componente = 3

                        if valor > 500:
                            alerta = 1



                    comando_sql = """
                        INSERT INTO leitura 
                        (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, fk_alerta,dia_hora) 
                        VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
                    
                                    
                    valores = (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, alerta)
                                    
                    cursor.execute(comando_sql, valores)
                db.commit()
                                    
                t.sleep(3)



            except KeyboardInterrupt:
                print("\nCaptura de CPU interrompida...\n")
                break



if __name__ == "__main__":
    menuCaptura(1)