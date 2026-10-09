# Lost & Found ENSAM Rabat

## Configuration

L'application nécessite une clé secrète pour signer les cookies de session. Générez
une clé et définissez-la dans l'environnement avant de lancer l'application :

```powershell
$env:SESSION_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
```

Ne partagez pas cette clé et ne la commitez pas dans le dépôt.
