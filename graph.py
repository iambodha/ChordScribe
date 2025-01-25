import matplotlib.pyplot as plt
import numpy as np

# Aktualisierte Daten
titel = ['Unser Layout', 'Dvorak', 'Colemak', 'QWERTY']
punkte = [66.79, 65.86, 65.83, 53.06]

# Distanzprozentsätze für die Finger
distanz_daten = {
    'Linker kleiner Finger': [18, 9, 7, 4],
    'Linker Ringfinger': [12, 4, 6, 3],
    'Linker Mittelfinger': [12, 1, 8, 16],
    'Linker Zeigefinger': [12, 21, 23, 25],
    'Linker Daumen': [0, 0, 0, 0],
    'Rechter Daumen': [0, 0, 0, 0],
    'Rechter Zeigefinger': [11, 25, 27, 24],
    'Rechter Mittelfinger': [10, 10, 10, 10],
    'Rechter Ringfinger': [12, 12, 5, 9],
    'Rechter kleiner Finger': [13, 18, 14, 9]
}

# Nutzungsprozentsätze für die Finger
nutzungs_daten = {
    'Linker kleiner Finger': [10, 9, 8, 7],
    'Linker Ringfinger': [10, 8, 6, 7],
    'Linker Mittelfinger': [9, 10, 7, 14],
    'Linker Zeigefinger': [12, 10, 16, 17],
    'Linker Daumen': [9, 9, 9, 9],
    'Rechter Daumen': [9, 9, 9, 9],
    'Rechter Zeigefinger': [9, 14, 16, 15],
    'Rechter Mittelfinger': [13, 11, 13, 7],
    'Rechter Ringfinger': [10, 9, 7, 10],
    'Rechter kleiner Finger': [9, 11, 9, 5]
}

# Farben für Konsistenz über die Diagramme hinweg
farben = ["#FF9999", "#66B2FF", "#99FF99", "#FFD966", "#FF66B2", "#A9A9F5", "#F5A9D0", "#8AD9B5", "#FF7F50", "#40E0D0"]

# Balkendiagramm für Punktzahlen
plt.figure(figsize=(10, 6))
plt.bar(titel, punkte, color=["#4CAF50", "#2196F3", "#FFC107", "#F44336"], edgecolor="black")
plt.title("Punktzahlen der Tastaturlayouts", fontsize=16)
plt.ylabel("Punktzahl", fontsize=14)
plt.xlabel("Tastaturlayout", fontsize=14)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("balkendiagramm_punktzahlen.png")
plt.show()

# Kreisdiagramme für Fingerabstände
fig, achsen = plt.subplots(2, 2, figsize=(15, 12))
achsen = achsen.flatten()
for i, achse in enumerate(achsen):
    abstände = [distanz_daten[finger][i] for finger in distanz_daten]
    achse.pie(abstände, labels=distanz_daten.keys(), autopct="%.1f%%", startangle=90, colors=farben)
    achse.set_title(f"{titel[i]} - Fingerabstände", fontsize=14)

fig.legend(distanz_daten.keys(), loc="center right", title="Finger", fontsize=12)
fig.suptitle("Fingerabstände nach Tastaturlayout", fontsize=16)
plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig("kreisdiagramm_abstaende.png")
plt.show()

# Gestapeltes Balkendiagramm für Fingernutzung
plt.figure(figsize=(14, 8))
finger = list(nutzungs_daten.keys())
nutzungs_prozente = np.array([nutzungs_daten[f] for f in finger])

unten = np.zeros(4)
for i, (f, prozente) in enumerate(zip(finger, nutzungs_prozente)):
    balken = plt.bar(titel, prozente, bottom=unten, label=f, color=farben[i], edgecolor='white')
    
    # Prozentangaben innerhalb jedes Balkensegments
    for j, b in enumerate(balken):
        höhe = prozente[j]
        if höhe > 0:
            plt.text(b.get_x() + b.get_width()/2., unten[j] + höhe/2.,
                     f'{höhe}%', ha='center', va='center', 
                     fontweight='bold', color='black')
    
    unten += prozente

plt.title("Fingernutzung nach Tastaturlayout", fontsize=16)
plt.xlabel("Tastaturlayout", fontsize=14)
plt.ylabel("Prozent der Nutzung", fontsize=14)
plt.legend(title="Finger", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig("gestapeltes_balkendiagramm_nutzung.png")
plt.show()

# Gestapeltes Balkendiagramm für Fingerabstände
plt.figure(figsize=(14, 8))
finger = list(distanz_daten.keys())
distanz_prozente = np.array([distanz_daten[f] for f in finger])

unten = np.zeros(4)
for i, (f, prozente) in enumerate(zip(finger, distanz_prozente)):
    balken = plt.bar(titel, prozente, bottom=unten, label=f, color=farben[i], edgecolor='white')
    
    # Prozentangaben innerhalb jedes Balkensegments
    for j, b in enumerate(balken):
        höhe = prozente[j]
        if höhe > 0:
            plt.text(b.get_x() + b.get_width()/2., unten[j] + höhe/2.,
                     f'{höhe}%', ha='center', va='center', 
                     fontweight='bold', color='black')
    
    unten += prozente

plt.title("Fingerabstände nach Tastaturlayout", fontsize=16)
plt.xlabel("Tastaturlayout", fontsize=14)
plt.ylabel("Prozent der Abstände", fontsize=14)
plt.legend(title="Finger", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig("gestapeltes_balkendiagramm_abstaende.png")
plt.show()
