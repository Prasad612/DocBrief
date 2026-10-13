# commands
docker run -d  --name jenkins  -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
docker run -d --name jenkins --security-opt seccomp=unconfined -p 8080:8080 -v /home/rhel/helm/Prasad/test-project/jenkins:/var/jenkins_home:Z jenkins/jenkins:lts-jdk17
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

sudo ctr -n k8s.io images import /tmp/myapp-test.tar
sudo ctr -n k8s.io images ls | grep myapp-test
kubectl rollout restart deployment/gen-docbrief -n deliver
kubectl get pods -n deliver -w

