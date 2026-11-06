from datetime import datetime
import time as t
import psutil as p
from mysql.connector import connection

# CPU: Uso da cpu:  p.cpu_percent; IoWait: cpu_times 
# DISCO: Uso do disco; Iops; 
# MEMÓRIA RAM: Uso da memória ram; Swap da ram; 

db = connection.MySQLConnection(
    host="44.206.205.13",
    port=3306,
    user="script_python",
    passwd="Sptech#2026",
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
Software de captura versão: 3.0
Data da última versão: 28-10-2026
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
                    bytes_leitura = iops_t2.read_bytes - iops_t1.read_bytes
                    bytes_escrita = iops_t2.write_bytes - iops_t1.write_bytes

                    mb_total = (bytes_leitura + bytes_escrita) / (1024 * 1024)
                    iops_total = mb_total / delta_tempo
                else:
                    iops_total = 0

                agora = datetime.now()
                data_formatada = agora.strftime("%d/%m/%Y")
                hora_atual = agora.strftime("%H:%M:%S")

                print("Data e Hora da Captura: ")
                print(data_formatada, hora_atual, '\n')

                for i in range(1, 8):

                    valor = 0.0
                    fk_unidade_medida = 0
                    alerta = 1
                    fk_metrica = 0
                    fk_componente = 0
                    
                    if i == 1:
                        valor = p.cpu_percent(interval=1)
                        fk_metrica = 1
                        fk_componente = 1
                        fk_unidade_medida = 1
                        
                        if valor > 50 and valor <= 70:
                            alerta = 2
                        elif valor >70:
                            alerta = 3

                    elif i == 2:
                        valor =  p.cpu_times_percent().softirq
                        fk_metrica = 2
                        fk_componente = 1
                        fk_unidade_medida = 1
                        
                        if valor > 0 and valor <= 5:
                            alerta = 2
                        elif valor > 5:
                            alerta = 3

                    elif i == 3:
                        valor = getattr(p.cpu_times(), 'iowait', 0.0)
                        fk_metrica = 3
                        fk_componente = 1
                        fk_unidade_medida = 2
                        
                        if valor > 0 and valor <= 0.3:
                            alerta = 2
                        elif valor > 0.3:
                            alerta = 3

                    elif i == 4:
                       valor = p.virtual_memory().percent
                       fk_metrica = 1
                       fk_componente = 2
                       fk_unidade_medida = 1

                       if valor > 40 and valor <= 65:
                        alerta = 2
                       elif valor > 65:
                        alerta = 3

                    elif i == 5:
                        valor = p.swap_memory().percent
                        fk_metrica = 4
                        fk_componente = 2
                        fk_unidade_medida = 1
                        
                        if valor > 0 and valor <= 3:
                            alerta = 2
                        elif valor > 3:
                            alerta = 3

                    elif i == 6:
                        valor = p.disk_usage('/').percent
                        fk_metrica = 1
                        fk_componente = 3
                        fk_unidade_medida = 1
                        
                        if valor > 30 and valor <= 65:
                            alerta = 2
                        elif valor > 65:
                            alerta = 3
                    
                    elif i == 7:
                        valor = iops_total
                        fk_metrica = 5
                        fk_componente = 3
                        fk_unidade_medida = 3

                        if valor > 500 and valor <= 800:
                            alerta = 2
                        elif valor > 800:
                            alerta =3 

                    comando_sql = """
                        INSERT INTO leitura 
                        (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida,dia_hora, fk_alerta) 
                        VALUES (%s, %s, %s, %s, %s, NOW(), %s)"""
                    
                                    
                    valores = (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, alerta)
                                    
                    cursor.execute(comando_sql, valores)
                db.commit()
                                    
                t.sleep(3)



            except KeyboardInterrupt:
                print("\nCaptura de CPU interrompida...\n")
                break


if __name__ == "__main__":
    menuCaptura(1)
