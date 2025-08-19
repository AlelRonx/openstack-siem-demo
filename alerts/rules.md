# Regole di rilevamento (SIEM Demo)

## Keystone brute force
- Condizione: >5 tentativi di login falliti dallo stesso IP in 1 minuto
- Query: `service : "keystone" and message : "*Authorization failed*"`

## Neutron - Creazione network
- Condizione: allerta su creazione di reti non autorizzate
- Query: `service : "neutron" and message : "*Added segment*" `

## Nova - Creazione VM
- Condizione: monitorare ogni nuova istanza creata
- Query: `service : "nova" and message : "*Instance spawned successfully*"`