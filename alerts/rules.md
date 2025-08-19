# Detection rules (SIEM Demo)

## Keystone brute force
- Condition: >5 failed login attempts from the same IP address within 1 minute
- Query: `service : "keystone" and message : "*Authorization failed*"`

## Neutron - Network creation
- Condition: monitor every new networks created
- Query: `service : "neutron" and message : "*Added segment*" `

## Nova - VM creation
- Condition: monitor every new instance created
- Query: `service : "nova" and message : "*Instance spawned successfully*"`
