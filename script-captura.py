from datetime import datetime
import os
import time as t
import psutil as p
import requests
from mysql.connector import connection

# Configurações do Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
CANAL_SLACK = "#low-latency"
COOLDOWN_SEGUNDOS = 300  # 5 minutos entre alertas iguais
ultimo_alerta = {}

METRICAS_INFO = {
    1: ("CPU", "Uso (%)", "%"),
    2: ("CPU", "Interrupcoes SW", "%"),
    3: ("CPU", "IOWait", "s"),
    4: ("RAM", "Uso (%)", "%"),
    5: ("RAM", "Uso SWAP (%)", "%"),
    6: ("Disco", "Uso (%)", "%"),
    7: ("Disco", "IOPS", "MB/s"),
}

def pode_notificar(fk_servidor: int, indice_metrica: int, nivel_alerta: int) -> bool:
    chave = (fk_servidor, indice_metrica, nivel_alerta)
    agora = t.time()
    if agora - ultimo_alerta.get(chave, 0) >= COOLDOWN_SEGUNDOS:
        ultimo_alerta[chave] = agora
        return True
    return False

def registrar_e_enviar_slack(
    cursor,
    fk_empresa: int,
    fk_servidor: int,
    indice_metrica: int,
    valor: float,
    nivel_alerta: int,
    data_hora: str
) -> None:
    if not pode_notificar(fk_servidor, indice_metrica, nivel_alerta):
        return

    componente, metrica, unidade = METRICAS_INFO.get(indice_metrica, ("Sistema", "Metrica", ""))
    status = "CRITICO" if nivel_alerta == 3 else "ALERTA"

    # 1. Grava na tabela slack do banco lowLatency (respeitando VARCHAR(45))
    titulo_db = f"[{status}] {componente} - {metrica}"[:45]
    conteudo_db = f"Srv #{fk_servidor}: {valor:.2f}{unidade} ({data_hora[11:]})"[:45]
    canal_db = CANAL_SLACK[:45]

    sql_slack = """
        INSERT INTO slack (titulo, conteudo, canal, fk_empresa)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql_slack, (titulo_db, conteudo_db, canal_db, fk_empresa))

    # 2. Envia a mensagem completa para o Webhook do Slack
    if not SLACK_WEBHOOK_URL:
        print("[AVISO] SLACK_WEBHOOK_URL não configurada; alerta salvo apenas no banco.")
        return

    payload = {
        "text": (
            f"*[{status}] Alerta lowLatency — Servidor #{fk_servidor}*\n"
            f"*Componente:* {componente}\n"
            f"*Métrica:* {metrica}\n"
            f"*Leitura:* `{valor:.2f} {unidade}`\n"
            f"*Data/Hora:* {data_hora}"
        )
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException as erro:
        print(f"[ERRO SLACK] Falha ao enviar para o Slack (registro salvo no MySQL): {erro}")

db = connection.MySQLConnection(
    host="52.201.30.147",
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

def menuCaptura(fk_servidor, fk_empresa=1):
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
                    elif valor > 70:
                        alerta = 3

                elif i == 2:
                    valor = p.cpu_times_percent().softirq
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
                        alerta = 3

                comando_sql = """
                    INSERT INTO leitura 
                    (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, dia_hora, fk_alerta) 
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s)"""
                
                valores = (fk_servidor, fk_componente, fk_metrica, valor, fk_unidade_medida, alerta)
                cursor.execute(comando_sql, valores)

                if alerta in (2, 3):
                    registrar_e_enviar_slack(
                        cursor=cursor,
                        fk_empresa=fk_empresa,
                        fk_servidor=fk_servidor,
                        indice_metrica=i,
                        valor=valor,
                        nivel_alerta=alerta,
                        data_hora=f"{data_formatada} {hora_atual}"
                    )

            db.commit()
            t.sleep(3)

        except KeyboardInterrupt:
            print("\nCaptura interrompida...\n")
            break

if __name__ == "__main__":
    menuCaptura(fk_servidor=1, fk_empresa=1)