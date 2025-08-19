SIEM Dashboard Integration with OpenStack (MicroStack) & ELK Stack

Questo progetto dimostra come integrare un’infrastruttura OpenStack (MicroStack) con uno stack SIEM basato su Elasticsearch, Logstash e Kibana (ELK).
L’obiettivo è raccogliere eventi e log dal cloud OpenStack, instradarli tramite Logstash ed elaborarli in Elasticsearch, con visualizzazione in Kibana.

Architettura degli strumenti usati:
OpenStack (MicroStack): ambiente cloud locale per il laboratorio.
Collector (collector.py): script Python che raccoglie eventi/log da OpenStack e li invia a Logstash.
Logstash: riceve i dati dal collector, li filtra e li inoltra ad Elasticsearch.
Elasticsearch: indicizza i log.
Kibana: dashboard interattiva per analizzare gli eventi.

Setup del progetto:
1.Installazione di MicroStack

$sudo snap install microstack --devmode --beta
$sudo microstack init --auto --control

Generazione della password di accesso alla piattaforma ed inserimento della sorgente .rc per le modifiche delle configurazioni di Openstack
$sudo snap get microstack config.credentials.keystone-password
$sudo source /var/snap/microstack/common/etc/microstack.rc

2.Creazione della rete di laboratorio ed un router dedicato su Openstack

$sudo openstack network create lab-net
$sudo openstack subnet create lab-subnet \
  --network lab-net \
  --subnet-range 10.20.20.0/24 \
  --gateway 10.20.20.1 \
  --dns-nameserver 8.8.8.8
$sudo openstack router create lab-router
$sudo openstack router set lab-router --external-gateway external
$sudo openstack router add subnet lab-router lab-subnet

3.Creazione della VM ELK

Scaricare l’immagine ufficiale Ubuntu desiderata dall'elenco (link a pie' di pagina):

$sudo wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

Si consiglia di intervenire sul file .img modificando le credenziali dell'immmagine
$sudo apt install guestfs-tools -y
$sudo virt-customize -a noble-server-cloudimg-amd64.img --password ubuntu:password:ubuntu
$sudo virt-customize -a noble-server-cloudimg-amd64.img -root-password password:password

Caricare l’immagine su MicroStack:

$sudo openstack image create "ubuntu-24.04-noble" \
  --file noble-server-cloudimg-amd64.img \
  --disk-format qcow2 \
  --container-format bare \
  --public

Si consiglia di modificare le regole nel Security Group per ELK aggiungendo regole sulle porte per elasticsearch(9200), kibana (5601), logstash (5000)

Creare la VM ELK su Compute:

$sudo openstack server create \
  --image ubuntu-24.04-noble \
  --flavor m1.high \
  --network lab-net \
  --security-group default \
  elk

Avviata l'istanza si consiglia di procedere in SSH sulla macchina in alternativa accedere alla console forita da Openstack
$sudo ssh -i /home/root/snap/microstack/common/.ssh/id_microstack root@10.20.20.47

Eventuali problematiche di negazione permesso di accesso possono essere risolte copiando la chiave pubblica di id_microstack in ~/.ssh/authorized_keys della VM "elk"

4.Setup dello stack ELK nella VM

Nella VM ELK installare Docker e avviare i servizi:

$sudo docker load -i elasticsearch-8.9.0.tar
$sudo docker load -i kibana-8.9.0.tar
$sudo docker load -i logstash-8.9.0.tar

$sudo docker-compose up -d

5.Configurazione file docker-compose.yml e json-opestack.conf

Il file docker-compose.yml configura i docker con i servizi utili al progetto mentre il file json-opestack.conf serve a Logstsh per rimanere in ascolto:

$sudo mkdir -p /opt/elk/logstash/pipeline/
$sudo cp docker-compose.yml /opt/elk/docker-compose.yml
$sudo cp json-opestack.conf /opt/elk/logstash/pipeline/json-opestack.conf

6.Collector (collector.py)

Lo script collector.py è il fulcro del progetto in quanto si connette a Keystone/OpenStack e raccoglie eventi di interesse (es. autenticazioni, creazione risorse), li converte in JSON e li invia a Logstash sulla porta 5000.
Deve essere avviato sulla macchina di Openstack

$sudo python3 collector.py

7.Risultato e limitazioni

Una volta avviato collector.py i log di keystone, Neutron e Nova vengono raccolti, inviati a Logstash, indicizzati in Elasticsearch e visualizzati in Kibana in una dashboard personalizzata.

Si consiglia di creare le macchine virutali con il minimo del seguente hardware:
VM Openstack => 16Gb Memory // 2/2 Processors // 100GB SCSI
VM Elk => 8Gb RAM // 2 Processors // 30GB Disk (attraverso creazione flavor personalizzato)

Inizialmente il progetto prevedeva la creazione di una Dashboard su Horizon sotto Project e collegata con la dashboard personalizzata di Kibana ma data la dipendenza a snap (read-only delle directory) di Microstack questo non e' stato possibile.
Eventuali file della creazione della dashboard sono stati comunque implementati ma non eseguiti.
E' possibile seguire la guida ufficiale per l'eventuale implementazione con differenti creazioni di Openstack

https://docs.openstack.org/horizon/latest/contributor/tutorials/dashboard.html

Documentazione di riferimento utilizzata per l'implementazione e la configurazione:
MicroStack Documentation
https://microstack.run/docs/
MicroStack CLI Reference
https://discourse.ubuntu.com/t/get-started-with-microstack/13998
Elastic Stack Docker Guide
https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic
OpenStack CLI Reference
https://docs.openstack.org/python-openstackclient/latest/


Questo README è sia guida all’uso che report sintetico del progetto nel periodo di Agosto 2025.
Nomi ed IP sono stati anonimizzati per la realizzazione del repository!
