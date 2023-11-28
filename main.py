import asyncio
import datetime
import os

import nacl.bindings
from helium_py.crypto.keypair import Keypair
from helium_py.crypto.keypair import SodiumKeyPair

from lib.helium import iot_config
from grpclib.client import Channel


async def main():
    host = os.getenv("HELIUM_HOST", default="mainnet-config.helium.io")
    port = os.getenv("HELIUM_PORT", default=6080)
    delegate_key_fname = os.getenv('HELIUM_KEYPAIR_BIN')
    if delegate_key_fname is None:
        print("env HELIUM_KEYPAIR_BIN is unfilled")
        return
    
    channel = Channel(host=host, port=port)
    service = iot_config.OrgStub(channel)
    response = await service.list(iot_config.OrgListReqV1())
    print(response)

    with open(delegate_key_fname, 'rb') as f:
        skey = f.read()[1:]
        delegate_keypair = Keypair(SodiumKeyPair(sk=skey,
                                                 pk=nacl.bindings.crypto_sign_ed25519_sk_to_pk(skey)))

    service = iot_config.RouteStub(channel)
    req = iot_config.RouteListReqV1(oui=1,
                                    timestamp=int(datetime.datetime.now(datetime.UTC).timestamp() * 1000),
                                    signer=delegate_keypair.address.bin)
    req.signature = delegate_keypair.sign(req.SerializeToString())
    resp = await service.list(req)
    print(resp)

    # req = iot_config.RouteCreateReqV1(oui=1,
    #                                   route=iot_config.RouteV1(oui=1,
    #                                                            id="something", net_id=0x000024, max_copies=5,
    #                                                            ignore_empty_skf=True,
    #                                                            server=iot_config.ServerV1(host="127.0.0.1",
    #                                                                                       port=12345,
    #                                                                                       gwmp=iot_config.ProtocolGwmpV1(
    #                                                                                           mapping=[
    #                                                                                               iot_config.ProtocolGwmpMappingV1(
    #                                                                                                   region=Region.EU868,
    #                                                                                                   port=1700)]))),
    #                                   timestamp=int(datetime.datetime.now(datetime.UTC).timestamp() * 1000),
    #                                   signer=delegate_keypair.address.bin)
    # req.signature = delegate_keypair.sign(req.SerializeToString())
    # resp = await service.create(req)
    # print(resp)

    req = iot_config.RouteListReqV1(oui=1,
                                    timestamp=int(datetime.datetime.now(datetime.UTC).timestamp() * 1000),
                                    signer=delegate_keypair.address.bin)
    req.signature = delegate_keypair.sign(req.SerializeToString())
    resp = await service.list(req)
    print(resp)

    # don't forget to close the channel when done!
    channel.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())