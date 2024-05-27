import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Conectar ao banco de dados (ou criar se não existir)
conn = sqlite3.connect('chamados.db')
cursor = conn.cursor()

# Certifique-se de que a tabela existe com as colunas corretas
cursor.execute('''
CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    data_abertura TEXT,
    data_fechamento TEXT,
    status TEXT,
    prioridade TEXT,
    tempo_resolucao REAL
)
''')

conn.commit()
conn.close()

# Funções para manipulação do banco de dados
def adicionar_chamado(descricao, data_abertura, prioridade):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO chamados (descricao, data_abertura, status, prioridade)
    VALUES (?, ?, ?, ?)
    ''', (descricao, data_abertura, 'Aberto', prioridade))
    
    conn.commit()
    conn.close()

def fechar_chamado(id_chamado):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    
    data_fechamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('SELECT data_abertura FROM chamados WHERE id = ?', (id_chamado,))
    data_abertura = cursor.fetchone()[0]
    tempo_resolucao = (datetime.strptime(data_fechamento, '%Y-%m-%d %H:%M:%S') - datetime.strptime(data_abertura, '%Y-%m-%d %H:%M:%S')).total_seconds() / 3600
    
    cursor.execute('''
    UPDATE chamados
    SET status = ?, data_fechamento = ?, tempo_resolucao = ?
    WHERE id = ?
    ''', ('Fechado', data_fechamento, tempo_resolucao, id_chamado))
    
    conn.commit()
    conn.close()

def atualizar_status(id_chamado, novo_status):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE chamados
    SET status = ?
    WHERE id = ?
    ''', (novo_status, id_chamado))
    
    conn.commit()
    conn.close()

def remover_chamado(id_chamado):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM chamados WHERE id = ?', (id_chamado,))
    
    conn.commit()
    conn.close()

def calcular_metricas():
    conn = sqlite3.connect('chamados.db')
    df = pd.read_sql_query('SELECT * FROM chamados', conn)
    conn.close()
    
    fechados = df[df['status'] == 'Fechado']
    
    if 'tempo_resolucao' in fechados.columns:
        tempo_medio_resolucao = fechados['tempo_resolucao'].mean()
    else:
        tempo_medio_resolucao = None
    
    numero_chamados_fechados = fechados.shape[0]
    numero_chamados_abertos = df[df['status'] == 'Aberto'].shape[0]
    
    return (tempo_medio_resolucao, numero_chamados_fechados, numero_chamados_abertos)

def listar_chamados():
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM chamados')
    rows = cursor.fetchall()
    
    conn.close()
    return rows

# Interface gráfica com Tkinter
class ChamadosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Chamados de TI")
        
        self.style = ttk.Style()
        self.style.configure('TLabel', padding=5)
        self.style.configure('TButton', padding=5)

        # Frame para adicionar chamados
        self.frame_add = ttk.LabelFrame(root, text="Adicionar Chamado", padding=10)
        self.frame_add.pack(padx=10, pady=10, fill="x", expand=True)
        
        self.descricao_label = ttk.Label(self.frame_add, text="Descrição:")
        self.descricao_label.grid(row=0, column=0, sticky="W")
        self.descricao_entry = ttk.Entry(self.frame_add, width=50)
        self.descricao_entry.grid(row=0, column=1)
        
        self.prioridade_label = ttk.Label(self.frame_add, text="Prioridade:")
        self.prioridade_label.grid(row=1, column=0, sticky="W")
        self.prioridade_entry = ttk.Entry(self.frame_add, width=20)
        self.prioridade_entry.grid(row=1, column=1, sticky="W")
        
        self.adicionar_button = ttk.Button(self.frame_add, text="Adicionar Chamado", command=self.adicionar_chamado_action)
        self.adicionar_button.grid(row=2, columnspan=2, pady=10)
        
        # Frame para atualizar/remover chamados
        self.frame_manage = ttk.LabelFrame(root, text="Gerenciar Chamado", padding=10)
        self.frame_manage.pack(padx=10, pady=10, fill="x", expand=True)
        
        self.id_label = ttk.Label(self.frame_manage, text="ID do Chamado:")
        self.id_label.grid(row=0, column=0, sticky="W")
        self.id_entry = ttk.Entry(self.frame_manage, width=20)
        self.id_entry.grid(row=0, column=1, sticky="W")
        
        self.status_label = ttk.Label(self.frame_manage, text="Novo Status:")
        self.status_label.grid(row=1, column=0, sticky="W")
        self.status_entry = ttk.Entry(self.frame_manage, width=20)
        self.status_entry.grid(row=1, column=1, sticky="W")
        
        self.atualizar_button = ttk.Button(self.frame_manage, text="Atualizar Status", command=self.atualizar_status_action)
        self.atualizar_button.grid(row=2, columnspan=2, pady=5)
        
        self.remover_button = ttk.Button(self.frame_manage, text="Remover Chamado", command=self.remover_chamado_action)
        self.remover_button.grid(row=3, columnspan=2, pady=5)
        
        # Frame para listar chamados
        self.frame_list = ttk.LabelFrame(root, text="Lista de Chamados", padding=10)
        self.frame_list.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tree = ttk.Treeview(self.frame_list, columns=("ID", "Descrição", "Data Abertura", "Data Fechamento", "Status", "Prioridade", "Tempo Resolução"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Data Abertura", text="Data Abertura")
        self.tree.heading("Data Fechamento", text="Data Fechamento")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Prioridade", text="Prioridade")
        self.tree.heading("Tempo Resolução", text="Tempo Resolução")
        
        self.tree.pack(fill="both", expand=True)
        self.atualizar_tabela()
        
        # Botão para visualizar métricas
        self.metricas_button = ttk.Button(root, text="Visualizar Métricas", command=self.mostrar_metricas)
        self.metricas_button.pack(padx=10, pady=10)

    def adicionar_chamado_action(self):
        descricao = self.descricao_entry.get()
        prioridade = self.prioridade_entry.get()
        data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if descricao and prioridade:
            adicionar_chamado(descricao, data_abertura, prioridade)
            messagebox.showinfo("Sucesso", "Chamado adicionado com sucesso!")
            self.atualizar_tabela()
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
        
        self.descricao_entry.delete(0, tk.END)
        self.prioridade_entry.delete(0, tk.END)

    def atualizar_status_action(self):
        id_chamado = self.id_entry.get()
        novo_status = self.status_entry.get()
        
        if id_chamado and novo_status:
            atualizar_status(id_chamado, novo_status)
            messagebox.showinfo("Sucesso", "Status do chamado atualizado com sucesso!")
            self.atualizar_tabela()
        else:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
        
        self.id_entry.delete(0, tk.END)
        self.status_entry.delete(0, tk.END)

    def remover_chamado_action(self):
        id_chamado = self.id_entry.get()
        
        if id_chamado:
            remover_chamado(id_chamado)
            messagebox.showinfo("Sucesso", "Chamado removido com sucesso!")
            self.atualizar_tabela()
        else:
            messagebox.showwarning("Atenção", "Preencha o ID do chamado.")
        
        self.id_entry.delete(0, tk.END)

    def mostrar_metricas(self):
        metricas = calcular_metricas()
        messagebox.showinfo("Métricas",
                            f"Tempo médio de resolução: {metricas[0]:.2f} horas\n"
                            f"Número de chamados fechados: {metricas[1]}\n"
                            f"Número de chamados abertos: {metricas[2]}")
        self.visualizar_metricas()

    def visualizar_metricas(self):
        conn = sqlite3.connect('chamados.db')
        df = pd.read_sql_query('SELECT * FROM chamados', conn)
        conn.close()
        
        fechados = df[df['status'] == 'Fechado']
        
        if 'tempo_resolucao' in fechados.columns and not fechados.empty:
            plt.figure(figsize=(10, 5))
            sns.histplot(fechados['tempo_resolucao'], bins=10, kde=True)
            plt.title('Distribuição do Tempo de Resolução dos Chamados')
            plt.xlabel('Tempo de Resolução (horas)')
            plt.ylabel('Frequência')
            plt.show()
        else:
            messagebox.showwarning("Atenção", "Nenhum dado de tempo de resolução disponível.")

    def atualizar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in listar_chamados():
            self.tree.insert("", "end", values=row)

# Configuração da janela principal do Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = ChamadosApp(root)
    root.mainloop()
