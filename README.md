SIEM Dashboard Integration with OpenStack (MicroStack) & ELK Stack

This project demonstrates how to integrate an OpenStack infrastructure (MicroStack) with a SIEM stack based on Elasticsearch, Logstash, and Kibana (ELK).
The goal is to collect events and logs from the OpenStack cloud, route them through Logstash, and process them in Elasticsearch, with visualization in Kibana.

Architecture of the tools used:
OpenStack (MicroStack): local cloud environment for the laboratory.
Collector (collector.py): Python script that collects events/logs from OpenStack and sends them to Logstash.
Logstash: receives data from the collector, filters it, and forwards it to Elasticsearch.
Elasticsearch: indexes the logs.
Kibana: interactive dashboard for analyzing events.

Project setup:
1. Installation of MicroStack
$sudo snap install microstack --devmode --beta
$sudo microstack init --auto --control

Generation of the platform access password and insertion of the "*.rc" source for changes to Openstack configurations
$sudo snap get microstack config.credentials.keystone-password
$sudo source /var/snap/microstack/common/etc/microstack.rc

2. Creation of the laboratory network and a dedicated router on Openstack
$sudo openstack network create lab-net
$sudo openstack subnet create lab-subnet \
  --network lab-net \
  --subnet-range 10.20.20.0/24 \
  --gateway 10.20.20.1 \
  --dns-nameserver 8.8.8.8
$sudo openstack router create lab-router
$sudo openstack router set lab-router --external-gateway external
$sudo openstack router add subnet lab-router lab-subnet

3. Creating the ELK VM
Download the desired official Ubuntu image from the list (link at the bottom of the page):
$sudo wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

I recommend modifying the "*.img" file by changing the image credentials.
$sudo apt install guestfs-tools -y
$sudo virt-customize -a noble-server-cloudimg-amd64.img --password ubuntu:password:ubuntu
$sudo virt-customize -a noble-server-cloudimg-amd64.img -root-password password:password

Upload the image to OpenStack:
$sudo openstack image create "ubuntu-24.04-noble" \
  --file noble-server-cloudimg-amd64.img \
  --disk-format qcow2 \
  --container-format bare \
  --public

I recommend modifying the rules in the "Security Group" for ELK by adding access rules on ports for elasticsearch (9200), kibana (5601), and logstash (5000).

Create the ELK VM on OpenStack Compute:
$sudo openstack server create \
  --image ubuntu-24.04-noble \
  --flavor m1.high \
  --network lab-net \
  --security-group default \
  elk

Once the instance has been started, I recommend proceeding via SSH on the machine or, alternatively, accessing the console provided by Openstack.
$sudo ssh -i /home/root/snap/microstack/common/.ssh/id_microstack root@10.20.20.47

Any issues with access "permission denial" can be resolved by copying the public key of id_microstack to ~/.ssh/authorized_keys of the ELK VM.

4. Setting up the ELK stack in the VM
In the ELK VM, install Docker and start the services:
$sudo docker load -i elasticsearch-8.9.0.tar
$sudo docker load -i kibana-8.9.0.tar
$sudo docker load -i logstash-8.9.0.tar

$sudo docker-compose up -d

5. Configuration of docker-compose.yml and json-opestack.conf files
The docker-compose.yml file configures the dockers with the services useful for the project, while the json-opestack.conf file is used by Logstsh to remain listening:
$sudo mkdir -p /opt/elk/logstash/pipeline/
$sudo cp docker-compose.yml /opt/elk/docker-compose.yml
$sudo cp json-opestack.conf /opt/elk/logstash/pipeline/json-opestack.conf

6.Collector (collector.py)
The collector.py script is the core of the project as it connects to SIEM and collects events of interest (e.g., authentications, resource creation), converts them to JSON, and sends them to Logstash on port 5000.
collector.py must be started on the Openstack machine where OpenStack is installed.
$sudo python3 collector.py

7. Results and limitations
Once collector.py is launched, the Keystone, Neutron, and Nova logs are collected, sent to Logstash, indexed in Elasticsearch, and displayed in Kibana in a custom dashboard thanks to the rules implemented in Kibana.

I recommend creating virtual machines with the minimum of the following hardware:
VM Openstack => 16Gb Memory // 2/2 Processors // 100Gb SCSI
VM ELK => 8Gb RAM // 2 Processors // 30Gb Disk (through custom flavor creation)

Initially, the project involved creating a Dashboard on Horizon under Project and linking it to Kibana's custom dashboard, but given Microstack's dependence on snap (read-only directories), this was not possible.
Any files related to the creation of the dashboard were implemented but not executed.
You can follow the official guide for possible implementation with different Openstack creations.

https://docs.openstack.org/horizon/latest/contributor/tutorials/dashboard.html

Reference documentation used for implementation and configuration:
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
