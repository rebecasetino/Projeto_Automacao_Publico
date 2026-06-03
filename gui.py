import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import shutil
import os
import sys

# garante que o diretório de trabalho é sempre onde o .exe está
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


# ── cores e fontes ──────────────────────────────────────────────
BG        = "#0f0f0f"
PANEL     = "#1a1a1a"
BORDER    = "#2a2a2a"
ACCENT    = "#d4a843"
ACCENT2   = "#b8922e"
TEXT      = "#f0ece0"
MUTED     = "#6b6560"
SUCCESS   = "#4caf7d"
ERROR     = "#e05c5c"
FONT_MONO = ("Consolas", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 13, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conferência de criterio_1s")
        self.geometry("680x620")
        self.resizable(True, True)
        self.minsize(600, 560)
        self.configure(bg=BG)

        self.arquivo_base = tk.StringVar(value="")
        self.captcha_event = threading.Event()
        self._build_ui()

    # ── construção da interface ──────────────────────────────────
    def _build_ui(self):
        # cabeçalho
        header = tk.Frame(self, bg=ACCENT, height=4)
        header.pack(fill="x")

        title_frame = tk.Frame(self, bg=BG, pady=18)
        title_frame.pack(fill="x", padx=30)
        tk.Label(title_frame, text="CONFERÊNCIA DE criterio_1S",
                 font=("Segoe UI", 14, "bold"), bg=BG, fg=ACCENT).pack(anchor="w")
        tk.Label(title_frame, text="Automação via portal Corretor Online",
                 font=FONT_UI, bg=BG, fg=MUTED).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # área de upload
        upload_frame = tk.Frame(self, bg=PANEL, padx=24, pady=16)
        upload_frame.pack(fill="x", padx=24, pady=(16, 0))

        tk.Label(upload_frame, text="PLANILHA BASE",
                 font=("Segoe UI", 9, "bold"), bg=PANEL, fg=MUTED).pack(anchor="w")

        row = tk.Frame(upload_frame, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))

        self.entry_arquivo = tk.Entry(
            row, textvariable=self.arquivo_base,
            font=FONT_MONO, bg="#111111", fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, state="readonly"
        )
        self.entry_arquivo.pack(side="left", fill="x", expand=True, ipady=7)

        btn_browse = tk.Button(
            row, text="  SELECIONAR  ",
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT, fg="#0f0f0f", activebackground=ACCENT2,
            activeforeground="#0f0f0f", relief="flat", cursor="hand2",
            command=self._selecionar_arquivo
        )
        btn_browse.pack(side="left", padx=(8, 0), ipady=7)

        # botões dentro do painel de upload
        btn_frame = tk.Frame(upload_frame, bg=PANEL, pady=(10))
        btn_frame.pack(fill="x", pady=(12, 0))

        self.btn_ok = tk.Button(
            btn_frame, text="▶  INICIAR",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT, fg="#0f0f0f", activebackground=ACCENT2,
            activeforeground="#0f0f0f", relief="flat", cursor="hand2",
            width=18, command=self._iniciar
        )
        self.btn_ok.pack(side="left", ipady=8)

        self.btn_captcha = tk.Button(
            btn_frame, text="✓  CAPTCHA RESOLVIDO",
            font=("Segoe UI", 10, "bold"),
            bg="#2a2a2a", fg=MUTED, relief="flat",
            width=24, state="disabled",
            command=self._confirmar_captcha
        )
        self.btn_captcha.pack(side="left", padx=(10, 0), ipady=8)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # área de log
        log_outer = tk.Frame(self, bg=BG, padx=24, pady=12)
        log_outer.pack(fill="both", expand=True)

        tk.Label(log_outer, text="LOG DE EXECUÇÃO",
                 font=("Segoe UI", 9, "bold"), bg=BG, fg=MUTED).pack(anchor="w")

        log_border = tk.Frame(log_outer, bg=BORDER, padx=1, pady=1)
        log_border.pack(fill="both", expand=True, pady=(6, 0))

        self.log_text = tk.Text(
            log_border, font=FONT_MONO, bg="#0a0a0a", fg=TEXT,
            relief="flat", state="disabled", wrap="word",
            insertbackground=ACCENT, selectbackground=ACCENT2
        )
        scroll = tk.Scrollbar(log_border, command=self.log_text.yview, bg=BORDER)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=6)

        # tags de cor no log
        self.log_text.tag_config("ok",      foreground=SUCCESS)
        self.log_text.tag_config("erro",    foreground=ERROR)
        self.log_text.tag_config("aviso",   foreground=ACCENT)
        self.log_text.tag_config("normal",  foreground=TEXT)
        self.log_text.tag_config("muted",   foreground=MUTED)

    # ── ações ────────────────────────────────────────────────────
    def _selecionar_arquivo(self):
        path = filedialog.askopenfilename(
            title="Selecione a planilha base",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
        )
        if path:
            self.arquivo_base.set(path)
            self._log(f"Arquivo selecionado: {os.path.basename(path)}", "ok")

    def _iniciar(self):
        if not self.arquivo_base.get():
            messagebox.showwarning("Atenção", "Selecione a planilha base antes de iniciar.")
            return

        self.btn_ok.config(state="disabled", bg=BORDER, fg=MUTED)
        self._log("Iniciando automação...", "aviso")
        threading.Thread(target=self._executar, daemon=True).start()

    def _confirmar_captcha(self):
        self.captcha_event.set()
        self.btn_captcha.config(state="disabled", bg=BORDER, fg=MUTED, text="✓  CAPTCHA RESOLVIDO")
        self._log("Captcha confirmado. Continuando...", "ok")

    def _executar(self):
        """Roda o main() do script adaptado para a GUI."""
        try:
            # copia o arquivo selecionado para base.xlsx no diretório do script
            origem = self.arquivo_base.get()
            destino = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), "base.xlsx")
            shutil.copy2(origem, destino)
            self._log("Planilha copiada como base.xlsx", "muted")

            # importa os módulos do projeto
            from navegador import (
                pesquisar_portal_e_preencher_login,
                switch_to_iframe_with_element,
                buscar_criterio_1, buscar_criterio_2,
                buscar_criterio_3,
                abrir_cadastro, verificar_campo_1,
                verificar_campo_2,
                verificar_campo_3,
                voltar_para_a_busca, mudar_tipo_busca,
            )
            from excel_utils import (
                ler_criterio_1s_excel_e_limpar,
                ler_criterio_2_excel,
                ler_criterio_3_excel,
                salvar_resultados_excel,
            )

            # login
            self._log("Abrindo portal e fazendo login...", "normal")
            pesquisar_portal_e_preencher_login()

            # aguarda captcha via botão
            self._log("⚠  Resolva o captcha e clique em 'CAPTCHA RESOLVIDO'.", "aviso")
            self.after(0, self._habilitar_captcha)
            self.captcha_event.wait()
            self.captcha_event.clear()

            # troca de frame
            try:
                switch_to_iframe_with_element("#Nocriterio_1Cia")
            except Exception as e:
                self._log(f"Aviso iframe: {e}", "aviso")

            criterio_1_validas, busca_criterio_2_criterio_1_nao_localizadas = ler_criterio_1s_excel_e_limpar()
            self._log(f"criterio_1s válidas encontradas: {len(criterio_1_validas)}", "ok")

            resultados_busca  = []
            itens_nao_localizados = []

            # busca por criterio_1
            for item in criterio_1_validas:
                numero_criterio_1 = item["criterio_1"]
                indice          = item["indice"]
                self._log(f"Consultando criterio_1 {numero_criterio_1}...", "muted")
                linha_cadastro = buscar_criterio_1(numero_criterio_1, busca_criterio_2_criterio_1_nao_localizadas, indice)
                if linha_cadastro:
                    abrir_cadastro(linha_cadastro)
                    grupo    = verificar_campo_1()
                    tipo     = verificar_campo_2()
                    campo_3 = verificar_campo_3()
                    resultados_busca.append({
                        "tipo_busca": "criterio_1", "chave": numero_criterio_1,
                        "campo_1": grupo or "", "campo_2": tipo or "",
                        "campo_3": campo_3 or "", "resultado_final": "LOCALIZADO",
                    })
                    self._log(f"  ✓ {numero_criterio_1} localizada", "ok")
                    voltar_para_a_busca()
                else:
                    resultados_busca.append({
                        "tipo_busca": "criterio_1", "chave": numero_criterio_1,
                        "campo_1": "", "campo_2": "", "campo_3": "",
                        "criterio_1_buscado": "NAO LOCALIZADA",
                    })
                    self._log(f"  ✗ {numero_criterio_1} não localizada", "erro")

            # busca por criterio_2
            criterio_2_validos, busca_nome, df = ler_criterio_2_excel(busca_criterio_2_criterio_1_nao_localizadas)
            self._log(f"criterio_2 válidos: {len(criterio_2_validos)}", "ok")

            if criterio_2_validos:
                mudar_tipo_busca("criterio_2")
                for item in criterio_2_validos:
                    criterio_2 = item["criterio_2"]
                    indice = item["indice"]
                    self._log(f"Consultando criterio_2 {criterio_2}...", "muted")
                    linha_cadastro = buscar_criterio_2(criterio_2, busca_nome, df, indice)
                    if linha_cadastro:
                        abrir_cadastro(linha_cadastro)
                        grupo    = verificar_campo_1()
                        tipo     = verificar_campo_2()
                        campo_3 = verificar_campo_3()
                        resultados_busca.append({
                            "tipo_busca": "criterio_2", "chave": criterio_2,
                            "campo_1": grupo or "", "campo_2": tipo or "",
                            "campo_3": campo_3 or "", "resultado_final": "LOCALIZADO",
                        })
                        self._log(f"  ✓ criterio_2 {criterio_2} localizado", "ok")
                        voltar_para_a_busca()
                    else:
                        resultados_busca.append({
                            "tipo_busca": "criterio_2", "chave": criterio_2,
                            "campo_1": "", "campo_2": "", "campo_3": "",
                            "criterio_2_buscado": "NAO LOCALIZADO",
                        })
                        self._log(f"  ✗ criterio_2 {criterio_2} não localizado", "erro")

            # busca por nome/razão social
            nome_validos, itens_nao_localizados, df = ler_criterio_3_excel(busca_nome)
            self._log(f"Nomes/Razões sociais: {len(nome_validos)}", "ok")

            if nome_validos:
                mudar_tipo_busca("criterio_3")
                for item in nome_validos:
                    nome   = item["criterio_3"]
                    indice = item["indice"]
                    self._log(f"Consultando nome {nome}...", "muted")
                    resultado = buscar_criterio_3(nome, itens_nao_localizados, df, indice)
                    if isinstance(resultado, tuple):
                        linha_cadastro, status = resultado
                    else:
                        linha_cadastro, status = None, "NAO LOCALIZADO"

                    if status == "LOCALIZADO" and linha_cadastro:
                        abrir_cadastro(linha_cadastro)
                        grupo    = verificar_campo_1()
                        tipo     = verificar_campo_2()
                        campo_3 = verificar_campo_3()
                        resultados_busca.append({
                            "tipo_busca": "nome", "chave": nome,
                            "campo_1": grupo or "", "campo_2": tipo or "",
                            "campo_3": campo_3 or "", "resultado_final": "LOCALIZADO",
                        })
                        self._log(f"  ✓ {nome} localizado", "ok")
                        voltar_para_a_busca()
                    elif status == "INICIO VIGENCIA IGUAL, PRODUTO DIFERENTE":
                        resultados_busca.append({
                            "tipo_busca": "nome", "chave": nome,
                            "campo_1": "", "campo_2": "", "campo_3": "",
                            "resultado_final": "INICIO VIGENCIA IGUAL, PRODUTO DIFERENTE",
                        })
                        self._log(f"  ~ {nome}: vigência igual, produto diferente", "aviso")
                    else:
                        resultados_busca.append({
                            "tipo_busca": "nome", "chave": nome,
                            "campo_1": "", "campo_2": "", "campo_3": "",
                            "resultado_final": "NAO LOCALIZADO",
                        })
                        self._log(f"  ✗ {nome} não localizado", "erro")

            # salva resultado
            salvar_resultados_excel(resultados_busca, itens_nao_localizados)
            self._mover_para_downloads()

        except Exception as e:
            self._log(f"ERRO: {e}", "erro")
            try:
                from excel_utils import salvar_resultados_excel
                salvar_resultados_excel(resultados_busca, itens_nao_localizados)
                self._mover_para_downloads()
            except Exception:
                pass
        finally:
            self.after(0, lambda: self.btn_ok.config(
                state="normal", bg=ACCENT, fg="#0f0f0f"))

    def _mover_para_downloads(self):
        """Move base_conferida.xlsx para a pasta Downloads do usuário."""
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        origem = os.path.join(base_dir, "base_conferida.xlsx")
        downloads = os.path.join(os.path.expanduser("~"), "Downloads", "base_conferida.xlsx")
        if os.path.exists(origem):
            shutil.move(origem, downloads)
            self._log(f"✓ Arquivo salvo em: {downloads}", "ok")
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"base_conferida.xlsx salvo em:\n{downloads}"))
        else:
            self._log("Arquivo base_conferida.xlsx não encontrado após execução.", "erro")

    def _habilitar_captcha(self):
        self.btn_captcha.config(
            state="normal", bg=ACCENT, fg="#0f0f0f",
            activebackground=ACCENT2, cursor="hand2",
            text="✓  CAPTCHA RESOLVIDO"
        )

    def _log(self, mensagem, tag="normal"):
        def _append():
            self.log_text.config(state="normal")
            self.log_text.insert("end", mensagem + "\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.after(0, _append)


if __name__ == "__main__":
    app = App()
    app.mainloop()
