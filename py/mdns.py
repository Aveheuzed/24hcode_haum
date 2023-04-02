from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from time import sleep

_tab = dict()


class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        _tab[name.split('.')[0]] = ".".join(str(val) for val in [info.addresses[0][i] for i in range(0, len(info.addresses[0]))])


def dnsquery():
    ##return {"CarNode-Simu2":"192.168.24.123"}
    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_carnode._udp.local.", listener)

    while not len(_tab):
        sleep(0.1)

    sleep(10)
    return _tab
