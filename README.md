# W4 SEO-Skills für Claude Code

Drei Skills für SEO-Arbeit mit Claude Code:

| Skill | Zweck |
|---|---|
| `gsc-indexation-audit` | Prüft, welche URLs einer Site tatsächlich im Google-Index sind, und stösst die Indexierung fehlender Seiten an (Sitemap-Sweep über die URL Inspection API, Ergebnis-Sheet, tägliche Verifikation). |
| `seo-keyword-research` | Komplette Keyword-Recherche-Pipeline: Business-Verständnis, Seed-Keywords, Expansion über Ahrefs, Harvest der Rankings von Client und 3 Wettbewerbern, Merge in eine Master-Liste, Pruning nach Relevanz. |
| `marketingblatt-content-engine` | Recherchiert und schreibt deutsche B2B-Blogartikel: SERP- und Intent-Recherche, Kannibalisierungs-Check, Entity-Gap-Analyse der Top-Wettbewerber, verifizierte DACH-Statistiken, Abschnitt-für-Abschnitt-Draft mit Qualitäts-Gate. Lieferung als Google-Doc in Google Drive. |

## Installation

Voraussetzung: [Claude Code](https://claude.com/claude-code) ist installiert.

### Variante A: mit git

```bash
git clone https://github.com/davidkoehler-elevalo/w4-seo-skills.git
cd w4-seo-skills
mkdir -p ~/.claude/skills
cp -R gsc-indexation-audit seo-keyword-research marketingblatt-content-engine ~/.claude/skills/
```

### Variante B: ohne git (ZIP)

1. Oben auf dieser Seite: **Code → Download ZIP**
2. ZIP entpacken
3. Die drei Skill-Ordner nach `~/.claude/skills/` kopieren (im Finder: `Cmd+Shift+G`, dann `~/.claude/skills` eingeben; Ordner ggf. vorher anlegen)

Danach eine **neue Claude-Code-Session** starten. Die Skills werden beim Start automatisch geladen und lassen sich per Namen oder passender Anfrage aufrufen (z. B. "Indexierung von example.com prüfen" oder "Keyword-Recherche für example.com").

## Zugänge, die die Skills zur Laufzeit brauchen

Die Installation selbst braucht nichts weiter. Beim ersten Aufruf fragen die Skills nach den Zugängen, die sie für die jeweilige Aufgabe benötigen:

- **gsc-indexation-audit:** Google-Konto mit Search-Console-Zugriff auf die Property, Google-Cloud-Auth (ADC) für die URL Inspection API
- **seo-keyword-research:** Ahrefs-Zugang sowie Search-Console-Zugriff auf die untersuchten Domains
- **marketingblatt-content-engine:** Google-Drive/Docs-Auth für die Ablieferung, API-Keys für Google NLP und Knowledge Graph

Details stehen jeweils in der `SKILL.md` des Skills.

## Updates

Bei einer neuen Version: Repository aktualisieren (`git pull` bzw. ZIP neu laden) und die drei Ordner erneut nach `~/.claude/skills/` kopieren. Eigene Anpassungen an den Skills vorher sichern, gleichnamige Dateien werden überschrieben.
