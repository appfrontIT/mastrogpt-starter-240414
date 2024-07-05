# Setup

In order to setup Walkiria Cluster you need:
    - 3 VM + 1 that works as the control service. We will call this 'bastion' from now on. It's advised to have ipv4 address on the bastion and on 1 VM
    - This guide is intended for VM running Ubuntu 22.04
    
## Step 1

First, you need to ssh inside the bastion using as root, using the ipv4 of the VM and the root password;
```
ssh root@<bastion ip>
```
insert the password. Then create a public ssh with:
```
ssh-keygen -t rsa
```
You’ll be prompted with a request on where to save the newly-created files.
The best option here is to type Enter and place the keys in their default location.
The public key (the one you may share) is located at /home/local-user/.ssh/id_rsa.pub . The private key is located at /home/local-user/.ssh/id_rsa

copy you id_rsa.pub inside the authorized_keys:
```
cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys
```

At this point, you can reinstall the others VMs adding the you public ssh to them.
Another way, is to manually authorize this key from inside each server. While still sshed in the bastion, do these steps:
    - log into each server using ssh root@<server ip>. For the 2 VMs without the ipv4, using the -6 flag
```
ssh -6 root@<server ip>
```
    - copy the key inside the authorized_keys, in the .ssh folder
```
cat >> ~/.ssh/authorized_keys
```
    and paste your key here. Logout and go to next VM.
    <!-- - you can also use this command to ease the process:
    ```
    cat ~/.ssh/id_rsa.pub | ssh root@remote_server "cat >> ~/.ssh/authorized_keys"
    ``` -->
    <!-- where you must change remote_server with each server and add '-6' flag for the ipv6 address -->

## Step 2

Now we need to set up the environment to install nuvolaris cluster. Inside the bastion launch the following commands:
    - update the system
``` 
apt-get update
```
    - install git and snapd
```
apt-get install git snapd
```
    - clone grinder from nuvolaris
```
git clone git@github.com:nuvolaris/grinder
```
    - cd into grinder
```
cd grinder/
```
    - update submodule
```
git submodule update --init --force --remote
```

## Step 3

We can start with the installation now:
    - inside grinder folder, launch setup.sh
```
bash setup.sh
```
keep in mind that many of the following steps will take a LOT of time, so be patient. This script will setup the environment for each VM.
    - create the .env from the .env.dist
```
cp .env.dist .env
```
    - delete everything except: DOCKER_HUB_USER, DOCKER_HUB_TOKEN, SLACK_API_URL, SLACK_CHANNEL
    - now you need to fill the .env with your data, especially DOCKER_HUB_USER, DOCKER_HUB_TOKEN
    - if you want to send notification to your slack, you must build an app in Slack and put the link in 'SLACK_API_URL' and the channel in 'SLACK_CHANNEL'
    - we need to setup the config/appfront.env:
        - change NUV_DOMAIN to the domain it needs to point (walkiria.cloud)
        - below NUV_DOMAIN add NUV_EMAIL and put your email there to configure the ssl later
        - set GW_PUBLIC_IP to your bastion ipv4 address, GW_IPV4 must be 10.1.88.1, GW_IPV6 you bastion ipv6 without the subnet mask
        - delete GW_CADDY line
        - change SERVER_PRIMARY_IP to 10.1.88.1
        - change REMOTE_NAME_1 with your remote name(appfront)
        - change REMOTE_IPV6_1 with the ipv6 of the bastion without the subnet mask
        - remove the last 5 lines (GATEWAY_WG, SERVER_WG_1, SERVER_WG_2, SERVER_WG_3 REMOTE_WG_1)
    - now reload the ENV by closing and reoping the terminal or launching:
```
source ~/.bashrc
```
    - inside grinder folder, launch
```
task config C=appfront
```
    - at the of the execution, you will find the 5 ENV vars we delete before. Copy and paste them inside the config/appfront.env
    - inside grinder folder, launch:
```
task setup:wireguard
```
    this will take a REALLY LONG time.
    - when it finished, launch the following command:
```
task status:vms
```
    you will see that the disk is not partitioned. To correctly use 'rook' we need a dedicated partion. Launch the following command to partition all the VMs:
```
task setup:repartition
```
    - setup the cluster:
```
task setup:cluster
```
    - check the cluster status:
```
task status:cluster
```
    if everything is fine, you should see 3 nodes

## Step 4

We're almost done.
First of all, we need to ensure the rook status:
```
task status:rook
```
This command will fail several times. Keep launching it until everything is fine. It's a known bug we need to fix.
When rook returns fine, let's start a watcher to control the installation status:
```
watch kubectl -n nuvolaris get po
```
open this in a new terminal, so you can keep controlling it while finishing the installation

Finally, launch the following command:
```
task setup:enterprise
```
You will start seeing the services being installing from the watcher. This operation takes some time as well, but it's the last one.
the setup:enterpise will probably timeout. This is a known issue and doesn't affects the installation. Just wait and don't run the command again.

When all the services are running, visit your hostname and you will find a message from nuvolaris.

Now launch the login setup:
```
nuv setup nuvolaris login
```
Activate all services by launching
```
nuv config enable --all
```
wait until it finished. Now you can add a namespace and use it by launching:
```
nuv admin adduser <username> <email> <password> --all
```
Try to login with nuv -login <host> <username>, than insert the password when it's prompted
