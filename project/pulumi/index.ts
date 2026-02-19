import * as fs from "node:fs";
import * as path from "node:path";

import * as pulumi from "@pulumi/pulumi";
import * as yandex from "@pulumi/yandex";

const config = new pulumi.Config();
const yandexConfig = new pulumi.Config("yandex");

const zone = config.get("zone") ?? yandexConfig.get("zone") ?? "ru-central1-a";

const instanceName = config.get("instanceName") ?? "lab04-vm";
const subnetCidr = config.get("subnetCidr") ?? "10.10.0.0/24";

const sshUsername = config.get("sshUsername") ?? "ubuntu";
const sshPublicKeyPath =
  config.get("sshPublicKeyPath") ?? "../terraform/certs/devops.pub";

const imageId = config.require("imageId");
const platformId = config.get("platformId") ?? "standard-v2";

const cores = config.getNumber("cores") ?? 2;
const coreFraction = config.getNumber("coreFraction") ?? 20;
const memoryGb = config.getNumber("memoryGb") ?? 1;

const diskSizeGb = config.getNumber("diskSizeGb") ?? 15;
const diskType = config.get("diskType") ?? "network-hdd";

const labels: Record<string, string> = {
  lab: "lab04",
  iac: "pulumi",
};

const sshPublicKey = fs
  .readFileSync(path.resolve(__dirname, sshPublicKeyPath), "utf-8")
  .trim();

const network = new yandex.VpcNetwork(`${instanceName}-net`, {
  labels,
  name: `${instanceName}-net`,
});

const subnet = new yandex.VpcSubnet(`${instanceName}-subnet`, {
  labels,
  name: `${instanceName}-subnet`,
  networkId: network.id,
  v4CidrBlocks: [subnetCidr],
  zone,
});

const securityGroup = new yandex.VpcSecurityGroup(`${instanceName}-sg`, {
  labels,
  name: `${instanceName}-sg`,
  networkId: network.id,
  ingresses: [
    {
      description: "SSH",
      protocol: "TCP",
      port: 22,
      v4CidrBlocks: ["0.0.0.0/0"],
    },
    {
      description: "HTTP",
      protocol: "TCP",
      port: 80,
      v4CidrBlocks: ["0.0.0.0/0"],
    },
  ],
  egresses: [
    {
      description: "Allow all outbound",
      protocol: "ANY",
      fromPort: 0,
      toPort: 65535,
      v4CidrBlocks: ["0.0.0.0/0"],
    },
  ],
});

const instance = new yandex.ComputeInstance(instanceName, {
  labels,
  name: instanceName,
  platformId,
  zone,
  resources: {
    cores,
    coreFraction,
    memory: memoryGb,
  },
  bootDisk: {
    initializeParams: {
      imageId,
      size: diskSizeGb,
      type: diskType,
    },
  },
  networkInterfaces: [
    {
      subnetId: subnet.id,
      nat: true,
      securityGroupIds: [securityGroup.id],
    },
  ],
  metadata: {
    "ssh-keys": `${sshUsername}:${sshPublicKey}`,
  },
});

const publicIp = instance.networkInterfaces.apply(
  (nis) => nis?.[0]?.natIpAddress,
);
const privateIp = instance.networkInterfaces.apply((nis) => nis?.[0]?.ipAddress);

export const vmPublicIp = publicIp;
export const vmPrivateIp = privateIp;
export const sshCommand = pulumi.interpolate`ssh ${sshUsername}@${publicIp}`;
