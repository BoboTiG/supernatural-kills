from supernatural import Supernatural

sn = Supernatural()
sn.download(force=True)
sn.parse()

sn.export_json()
