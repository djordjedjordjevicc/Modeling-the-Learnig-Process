import numpy as np
import matplotlib.pyplot as plt
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
import seaborn as sns
from fitter import Fitter, get_common_distributions

# Učitavanje podataka
comm_time_to_sec = np.loadtxt('commDurationS1.txt')

# Modeliranje mešovite raspodele sa Gaussian Mixture Model
n_components = 2
gmm = GaussianMixture(n_components=n_components)
gmm.fit(comm_time_to_sec.reshape(-1, 1))

# Vizualizacija rezultata
x = np.linspace(min(comm_time_to_sec), max(comm_time_to_sec), 1000).reshape(-1, 1)
y = np.exp(gmm.score_samples(x))

# Postavljanje boja za svaku komponentu
colors = sns.color_palette("husl", n_components)

plt.hist(comm_time_to_sec, bins=50, density=True, alpha=0.5, color='b', label='Histogram podataka')

# Prikaz pojedinačnih komponenata raspodele
for i in range(gmm.n_components):
    mean = gmm.means_[i][0]
    cov = np.sqrt(gmm.covariances_[i][0, 0])

    plt.plot(x, gmm.weights_[i] * norm.pdf(x, mean, cov), color=colors[i], label=f'Komponenta {i + 1}')

    # Analiza distribucija za svaku komponentu pomoću Fitter objekta
    f_component = Fitter(comm_time_to_sec[gmm.predict(comm_time_to_sec.reshape(-1, 1)) == i],
                         distributions=get_common_distributions())
    f_component.fit()

    # Ispis rezultata za svaku komponentu
    print(f"Rezultati za komponentu {i + 1} (nakon primene Fitter objekta):")
    print("  Težinski faktor (udeo komponente):", gmm.weights_[i])
    print("  Srednja vrednost komponente:", mean)
    print("  Standardna devijacija komponente:", cov)
    print("  Najbolja distribucija:", f_component.get_best())
    print("\n")

# Konačna mešovita raspodela
final_mixture = np.zeros_like(x)
for i in range(gmm.n_components):
    final_mixture += gmm.weights_[i] * norm.pdf(x, gmm.means_[i][0], np.sqrt(gmm.covariances_[i][0, 0]))

plt.plot(x, final_mixture, color='red', label='Konačna mešovita raspodela')

# Ispis rezultata za mešovitu raspodelu
print("\nRezultati za mešovitu raspodelu:")
print("AIC:", gmm.aic(comm_time_to_sec.reshape(-1, 1)))
print("BIC:", gmm.bic(comm_time_to_sec.reshape(-1, 1)))
print("Log-likelihood:", gmm.score(comm_time_to_sec.reshape(-1, 1)))


plt.legend()
plt.xlabel('Vreme u sekundama')
plt.ylabel('Učestalost')
plt.title('Mešovita raspodela')
plt.show()