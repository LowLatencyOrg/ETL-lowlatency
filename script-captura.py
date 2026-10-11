from datetime import datetime
import time as t
import psutil as p
import mysql.connector

# CPU: Uso da cpu:  p.cpu_percent; IoWait: cpu_times 
# DISCO: Uso do disco; Iops; 
# MEMÓRIA RAM: Uso da memória ram; Swap da ram; 

db = mysql.connector.connection.MySQLConnection(
    host="localhost",
    port=3306,
    user="root",
    passwd="", # falta add a senha do bd aqui
    database="lowLatency"
)

cursor = db.cursor()

print("\n_______________________________________________________________")

limite_atencao = 70 
limite_alerta = 90

def menuCaptura(fk_servidor):
        while True:
            selecao = int(input("\n Menu de Captura \n\n 1. CAPTURAR DADOS\n 2.VER HISTÓRICO \n 3.SAIR DO PROGRAMA: "))
            if selecao == 1:
                while True:
                    try:
                        iops_t1 = p.disk_io_counters()
                        iops_t2 = p.disk_io_counters()

                        agora = datetime.now()
                        data_formatada = agora.strftime("%d/%m/%Y")
                        hora_atual = agora.strftime("%H:%M:%S")

                        print("Data e Hora da Captura: ")
                        print(data_formatada, hora_atual, '\n')

                        for i in range(1, 7):
                                valor = 0.0
                                fk_unidade_medida = i
                                alerta = 0
                                fk_metrica = 0
                                fk_componente = 0
                                if i == 1:
                                    valor = p.cpu_percent(interval=0)
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
                                comando_sql = """
                            INSERT INTO leitura 
                            (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, alerta,dia_hora) 
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
                                
                                valores = (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, alerta)
                                
                                cursor.execute(comando_sql, valores)
                        db.commit()
                                
                        t.sleep(3)

                    except KeyboardInterrupt:
                        print("\nCaptura de CPU interrompida. Voltando ao menu...\n")
                        break

            #EM DESENVOLVIMENTO
            # elif selecao == 2:
            #     print(f"\nHistórico de Dados da Máquina (ID: {id})")

            #     cursor_dict = db.cursor(dictionary=True)

            #     comando_sql = """
            #         SELECT idRegistro, cpuPorcentagemUso, ramPercentualUso, discoEspacoUsado, downloadRede, uploadRede, statusGeral, dtRegistro 
            #         FROM registro 
            #         WHERE fkMaquina = %s 
            #         ORDER BY dtRegistro DESC 
            #         LIMIT 10
            #     """

            #     cursor_dict.execute(comando_sql, (id,))
            #     historico = cursor_dict.fetchall()

            #     if historico:
            #         print("\nÚltimos 10 registrs da máquina:")
            #         for registro in historico:
            #             data = registro['dtRegistro'].strftime("%d/%m/%Y %H:%M:%S") if registro['dtRegistro'] else "N/D"

            #             print(f"ID: {registro['idRegistro']} | CPU: {registro['cpuPorcentagemUso']}% | RAM: {registro['ramPercentualUso']}% | Disco: {registro['discoEspacoUsado']} GB | Download: {registro['downloadRede']} B | Upload: {registro['uploadRede']} B | Status: {registro['statusGeral']} | Data: {data}")
            #     else:
            #         print("\nNenhum histórico encontrado para esta Máquina no Banco de Dados.")

            #     cursor_dict.close()

            # elif selecao == 3:
            #     print("Saindo do Menu de Captura...")
            #     break

if __name__ == "__main__":
    menuCaptura(1)