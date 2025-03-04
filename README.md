# Face Recognition Using AWS

This repository contains the implementation of a **cloud-based face recognition system** using **Amazon Web Services (AWS)**. The project is divided into two parts:

- **Project 1: Infrastructure as a Service (IaaS)** – Implements an **auto-scaling face recognition system** using AWS EC2, SQS, and S3.
- **Project 2: Platform as a Service (PaaS)** – Implements a **serverless face recognition system** using AWS Lambda and S3.

## Table of Contents

- [Overview](#overview)
- [Project 1: IaaS Implementation](#project-1-iaas-implementation)
- [Project 2: PaaS Implementation](#project-2-paas-implementation)
- [Technology Stack](#technology-stack)
- [Setup and Deployment](#setup-and-deployment)
- [Contributors](#contributors)
- [License](#license)

## Overview

This project demonstrates how **cloud computing services** can be leveraged to build a **scalable and efficient face recognition system**. It explores both **Infrastructure as a Service (IaaS)** and **Platform as a Service (PaaS)** paradigms to implement an image and video-based face recognition pipeline using AWS.

---

## Project 1: IaaS Implementation

In this part, a **multi-tier cloud application** is implemented using AWS **EC2, SQS, and S3**. The system scales dynamically to handle increasing workloads by auto-scaling EC2 instances based on demand.

### Architecture
![Project 1 Architecture](Images/Screenshot%202025-03-03%20195538.png)
1. **Web Tier (EC2 Instance)**
   - Receives image files via HTTP POST requests.
   - Sends images to the **App Tier** using **AWS SQS (Request Queue)**.
   - Returns the **recognition results** from the App Tier.

2. **Application Tier (Auto-Scaling EC2 Instances)**
   - Retrieves image-processing tasks from **SQS Request Queue**.
   - Runs a **deep learning model** for face recognition using **PyTorch**.
   - Sends results back via **SQS Response Queue**.
   - Implements **auto-scaling**: Instances are launched based on request volume.

3. **Data Tier (S3 Buckets)**
   - Stores **input images** and **recognition results** for persistence.
   - Organized using AWS **key-value object storage**.

### Key Features

- **Auto-scaling** EC2 instances based on workload.
- **Queue-based messaging** between tiers using AWS SQS.
- **Efficient storage** of input and output data in AWS S3.
- **Machine learning-based face recognition** using PyTorch.

---

## Project 2: PaaS Implementation

This part transitions the face recognition pipeline into a **serverless architecture** using **AWS Lambda**. Instead of manually managing EC2 instances, **AWS Lambda** automatically executes functions in response to video uploads.

### Architecture
![Project 2 Architecture](Images/Screenshot%202025-03-03%20195559.png)
1. **AWS Lambda Function**
   - Triggered when a **video file** is uploaded to S3.
   - Uses **ffmpeg** to split videos into **frames (Group of Pictures - GoP)**.
   - Saves extracted frames into another **S3 bucket**.

2. **S3 Buckets**
   - **Input Bucket**: Stores uploaded videos.
   - **Stage-1 Bucket**: Stores extracted frames, named after the video filename.

### Key Features

- **Serverless architecture** with AWS Lambda.
- **Automated video frame extraction** using `ffmpeg`.
- **Highly scalable and cost-effective** without maintaining servers.

---

## Technology Stack

- **AWS Services:** EC2, SQS, S3, Lambda
- **Machine Learning:** PyTorch (Face Recognition Model)
- **Video Processing:** ffmpeg
- **Backend:** Python (Flask for Web Tier, Boto3 for AWS interaction)
- **Deployment:** Auto-Scaling Groups, Load Balancer, IAM Policies

---

## Setup and Deployment

### Project 1: IaaS Setup

1. **Launch the Web Tier (EC2 Instance)**
   - Run a Flask server to handle HTTP requests.
   - Configure **SQS queues** for request/response communication.

2. **Deploy the App Tier (Auto-Scaling EC2 Instances)**
   - Create an **AMI** with the deep learning model installed.
   - Set up **Auto Scaling Groups** with load balancing.

3. **Set Up Data Tier (S3 Buckets)**
   - Create **input** and **output buckets** for image storage.

### Project 2: PaaS Setup

1. **Create AWS Lambda Function**
   - Write a function to **split videos into frames** using `ffmpeg`.
   - Set up an **S3 trigger** to execute on video uploads.

2. **Configure S3 Buckets**
   - Input bucket for videos.
   - Stage-1 bucket for extracted frames.


