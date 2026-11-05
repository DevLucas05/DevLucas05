"""Gera linguagens.svg com as linguagens de todos os meus repositórios (públicos e privados).

Rodar: python linguagens.py   (precisa do gh logado com acesso aos repositórios privados)

ponytail: retrato estático, regerado à mão. Para atualizar sozinho, um workflow
agendado com um PAT de leitura nos secrets rodaria este mesmo script.
"""
import datetime
import json
import subprocess
from html import escape

DONO = "DevLucas05"
# venv commitado: os arquivos do pip inflam Python em ~4 MB
IGNORAR_REPOS = {"Organizador-de-Arquivos"}
# notebooks contam a saída das células; o resto é andaime gerado pelo Flutter e arquivos de config
IGNORAR_LINGUAGENS = {"Jupyter Notebook", "C", "C++", "CMake", "Objective-C", "Swift",
                      "Mako", "Procfile", "Dockerfile", "Batchfile", "Inno Setup"}
MAX_LINHAS = 8
CORES = {  # cores do GitHub Linguist
    "Go": "#00ADD8", "Dart": "#00B4AB", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#663399", "Ruby": "#701516",
    "Kotlin": "#A97BFF", "PowerShell": "#012456", "Shell": "#89e051", "Java": "#b07219",
    "C#": "#178600",
}


def gh(*args):
    return json.loads(subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout)


def somar_linguagens():
    repos = gh("repo", "list", DONO, "--source", "--limit", "200", "--json", "name")
    total = {}
    for repo in repos:
        if repo["name"] in IGNORAR_REPOS:
            continue
        for ling, bytes_ in gh("api", f"repos/{DONO}/{repo['name']}/languages").items():
            if ling not in IGNORAR_LINGUAGENS:
                total[ling] = total.get(ling, 0) + bytes_
    return total


def agrupar(total):
    soma = sum(total.values())
    ordem = sorted(total.items(), key=lambda kv: -kv[1])
    linhas = [(ling, b / soma) for ling, b in ordem[:MAX_LINHAS - 1]]
    resto = sum(b for _, b in ordem[MAX_LINHAS - 1:])
    if resto:
        linhas.append(("Outras", resto / soma))
    return linhas


def svg(linhas):
    largura, topo, passo = 480, 78, 26
    altura = topo + passo * len(linhas) + 30
    x_barra, larg_barra = 150, 250
    maior = max(p for _, p in linhas)
    pct = lambda p: f"{p * 100:.1f}%".replace(".", ",")
    descricao = ", ".join(f"{ling} {pct(p)}" for ling, p in linhas)
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    partes = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img">
<title>Linguagens que mais uso: {escape(descricao)}</title>
<style>
  text {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #1f2328; }}
  .sub, .rodape {{ fill: #59636e; }}
  .barra {{ fill: #0969da; }}
  @media (prefers-color-scheme: dark) {{
    text {{ fill: #f0f6fc; }}
    .sub, .rodape {{ fill: #9198a1; }}
    .barra {{ fill: #4493f8; }}
  }}
</style>
<text x="24" y="34" font-size="18" font-weight="600">Linguagens que mais uso</text>
<text class="sub" x="24" y="56" font-size="12">Volume de código em todos os meus repositórios, públicos e privados</text>''']

    for i, (ling, p) in enumerate(linhas):
        y = topo + i * passo
        cor = CORES.get(ling, "#8b949e")
        w = max(4, larg_barra * p / maior)
        partes.append(
            f'<circle cx="29" cy="{y + 9}" r="5" fill="{cor}"/>'
            f'<text x="42" y="{y + 13}" font-size="13">{escape(ling)}</text>'
            f'<rect class="barra" x="{x_barra}" y="{y + 5}" width="{w:.1f}" height="8" rx="4"/>'
            f'<text x="{largura - 24}" y="{y + 13}" font-size="13" text-anchor="end">{pct(p)}</text>'
        )
    partes.append(f'<text class="rodape" x="24" y="{altura - 14}" font-size="11">Atualizado em {hoje}</text>\n</svg>\n')
    return "\n".join(partes)


if __name__ == "__main__":
    linhas = agrupar(somar_linguagens())
    assert abs(sum(p for _, p in linhas) - 1) < 1e-9, "as porcentagens precisam somar 100%"
    with open("linguagens.svg", "w", encoding="utf-8") as f:
        f.write(svg(linhas))
    for ling, p in linhas:
        print(f"{ling:12} {p * 100:5.1f}%")
