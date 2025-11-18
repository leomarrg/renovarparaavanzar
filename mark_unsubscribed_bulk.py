#!/usr/bin/env python
"""
Script para marcar emails como dados de baja (unsubscribed)
Estos usuarios NO recibirán más emails en futuros envíos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from landing.models import Registration
from django.utils import timezone

# Lista de emails a dar de baja
EMAILS_TO_UNSUBSCRIBE = [
    "a_yoma@hotmail.com",
    "aarroyomd@hotmail.com",
    "acupuntura_1@yahoo.com",
    "aizoe@hotmail.com",
    "amnerysg@hotmail.com",
    "analiz_font@hotmail.com",
    "angeles.valentin@yahoo.com",
    "arnaldofreireperez@gmail.com",
    "arturo_arroba@hotmail.com",
    "billy@coquiviajero.com",
    "cacomo@hotmail.com",
    "calcupr@hotmail.com",
    "carled45@hotmail.com",
    "carlosmd64@hotmail.com",
    "carmen.dt@comcast.net",
    "carmin1943@hotmail.com",
    "carrasquillo_carmen@hotmail.com",
    "cesaralcantara42@hotmail.com",
    "cesarandinomd@hotmail.com",
    "cleryheughes@hotmail.com",
    "cobianed@hotmail.com",
    "coelurosaurs@hotmail.com",
    "cr.lopez@hotmail.com",
    "daberniermd@hotmail.com",
    "dalymary1520@hotmail.com",
    "daynasantiago92@hotmail.com",
    "devariediaz1959@live.com",
    "dioyi@hotmail.com",
    "diturrino@hotmail.com",
    "divadivine27@hotmail.com",
    "dr.joseorlandorivera@hotmail.com",
    "dr.nd@live.com",
    "dr.pablopastrana_@hotmail.com",
    "dr_riveravaldes@hotmail.com",
    "dra.ymendez@hotmail.com",
    "dra_casanova8@hotmail.com",
    "dra_gmieses@hotmail.com",
    "dracuautli@hotmail.com",
    "dranavarroin@hotmail.com",
    "drapsp@hotmail.com",
    "drasantos23@gmail.com",
    "drcastilloveitia1@hotmail.com",
    "drcruz61@yahoo.com",
    "drhectormmaldonado@hotmail.com",
    "drmboles@yahoo.com",
    "drsmonroig@hotmail.com",
    "drsylviaarce@hotmail.com",
    "drtitop@hotmail.com",
    "edcaquet60@hotmail.com",
    "edgargonzromero@hotmail.com",
    "ednaserranomd@gmail.com",
    "enriveramass@hotmail.com",
    "ericmauricio57@hotmail.com",
    "erojas@hotmail.com",
    "felfig48@hotmail.com",
    "francisco_rosado@hotmail.com",
    "gelpigyn@yahoo.com",
    "gladys_45@hotmail.com",
    "glomar201@hotmail.com",
    "grisellortiz@hotmail.com",
    "grodzmd@hotmail.com",
    "guiaur@hotmail.com",
    "guireida@hotmail.com",
    "hildamary@hotmail.com",
    "hildamorquecho_m@hotmail.com",
    "horidelfebomd@yahoo.com",
    "ibiza_y@yahoo.com",
    "ineshndez@hotmail.com",
    "ipey2008@hotmail.com",
    "iranziani@hotmail.com",
    "irisarzuaga@yahoo.com",
    "isa_mend4@hotmail.com",
    "ivanmontalvo@hotmail.com",
    "ivyadiaz.md@hotmail.com",
    "jagmagu@hotmail.com",
    "jarabelo@yahoo.com",
    "javigonzalez25@hotmail.com",
    "jbatistamd@hotmail.com",
    "jerm278@hotmail.com",
    "jocan2010@live.com",
    "joseperez12373@hotmail.com",
    "jtmp2010@hotmail.com",
    "jues510@hotmail.com",
    "jyrios@hotmail.com",
    "katiria35@hotmail.com",
    "lantomd@hotmail.com",
    "lassallec@hotmail.com",
    "lds247@msn.com",
    "lopezlinnette@hotmail.com",
    "luis.gerena@hotmail.com",
    "luisrcanetti@hotmail.com",
    "mariceltejeda@hotmail.com",
    "marie_diverse@live.com",
    "marielisluz@hotmail.com",
    "marielys@hotmail.com",
    "maryc974@hotmail.com",
    "maxguerrier@hotmail.com",
    "mayragonzalez5533@yahoo.com",
    "mdrodz@hotmail.com",
    "meilynr@hotmail.com",
    "mmuriente@hotmail.com",
    "momv0406@hotmail.com",
    "monge-jose@hotmail.com",
    "mulero-cardiacsurgery@hotmail.com",
    "murillo_md1@hotmail.com",
    "nautico3@hotmail.com",
    "naydagarcia2003@yahoo.com",
    "nestitorgt@hotmail.com",
    "nildatorres11@hotmail.com",
    "nuncorr@hotmail.com",
    "oficinadrdejesus@hotmail.com",
    "omartsi@hotmail.com",
    "omegajester@hotmail.com",
    "onicrespo@hotmail.com",
    "orcolon@universalpr.com",
    "ortiz_marie@hotmail.com",
    "pjdeleon@hotmail.com",
    "pjortizmd@hotmail.com",
    "pupi_manuel@msn.com",
    "qjacobo@gmail.com",
    "rafaelpepen19@hotmail.com",
    "ramon_sosa@hotmail.com",
    "ramonse490@hotmail.com",
    "rauldiazortiz@hotmail.com",
    "rgonzalez9353@hotmail.com",
    "ricardo_md04@hotmail.com",
    "ricardojrivasmd@hotmail.com",
    "rodneylopezmd@hotmail.com",
    "rosana_amador@hotmail.com",
    "santossamuel@hotmail.com",
    "setlantigua@hotmail.com",
    "silvinodiazmd@ahora.net",
    "tammyriboul@hotmail.com",
    "tania.falcon@cossma.org",
    "tonylozada@hotmail.com",
    "ttosado@hotmail.com",
    "vidal_feblesmd@live.com",
    "villar_felix@hotmail.com",
    "vmontesluquis@hotmail.com",
    "w_rodriguezh@hotmail.com",
    "wcelly@hotmail.com",
    "yarivale@hotmail.com",
    "yaslint@hotmail.com",
    "yjramos2@hotmail.com",
    "yoilisguerrero@yahoo.com",
    "yun_yun73@hotmail.com",
    "z_carrion@hotmail.com",
]

def mark_as_unsubscribed():
    """Marcar emails como dados de baja (NO recibirán más emails)"""
    print("=" * 60)
    print("MARCAR USUARIOS COMO DADOS DE BAJA")
    print("=" * 60)
    print()

    total = len(EMAILS_TO_UNSUBSCRIBE)
    print(f"Total de emails a dar de baja: {total}")
    print()

    updated = 0
    not_found = 0
    already_unsubscribed = 0

    for email in EMAILS_TO_UNSUBSCRIBE:
        email = email.strip().lower()

        # Buscar el registro
        registrations = Registration.objects.filter(email__iexact=email)

        if not registrations.exists():
            print(f"  ✗ {email} - No encontrado en la base de datos")
            not_found += 1
            continue

        # Verificar si ya está dado de baja
        if registrations.filter(unsubscribed=True).exists():
            print(f"  ○ {email} - Ya estaba dado de baja")
            already_unsubscribed += 1
            continue

        # Marcar como dado de baja
        count = registrations.update(
            unsubscribed=True,
            unsubscribed_at=timezone.now()
        )

        print(f"  ✓ {email} - Dado de baja ({count} registro(s))")
        updated += count

    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Total procesados:        {total}")
    print(f"✓ Dados de baja:         {updated}")
    print(f"○ Ya estaban de baja:    {already_unsubscribed}")
    print(f"✗ No encontrados:        {not_found}")
    print()
    print("✅ Estos emails NO recibirán más correos en futuros envíos.")
    print()

if __name__ == '__main__':
    print()
    print("⚠️  Este script marcará 147 emails como DADOS DE BAJA.")
    print("NO recibirán más emails cuando ejecutes send_email_sendgrid.py")
    print()
    print("¿Confirmas? (escribe SI):")

    if input().strip().upper() == 'SI':
        mark_as_unsubscribed()
    else:
        print("Operación cancelada.")
