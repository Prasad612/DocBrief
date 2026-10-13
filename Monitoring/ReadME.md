# OpenShift Monitoring with Prometheus and Grafana

## 1. Overview

Prometheus and Grafana were deployed on cluster to monitor Kubernetes resources in the deployment.

**Components used**

| Component | Purpose |
|---|---|
| Prometheus | Collects and stores monitoring metrics |
| Grafana | Visualizes metrics through dashboards and manages alerts |
| kube-state-metrics | Exposes Kubernetes object status metrics, such as pod readiness and container restarts |
| Node Exporter | Exposes node-level CPU, memory, and system metrics |
| Alertmanager | Handles alert notifications from Prometheus-based alerting |

**Monitoring objectives**
- Monitor CPU usage per pod.
- Monitor memory usage per pod.
- Track container restarts.
- Monitor pod readiness.
- Alert when a container restarts.

## 3. Install Prometheus and Grafana

### Step 1: Add the Helm repository

```bash
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts

helm repo update
```

### Step 2: Create the monitoring namespace and install

```bash
helm install monitoring \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

This installs the monitoring stack, including Prometheus, Grafana, Alertmanager, kube-state-metrics, and Node Exporter.

### Step 3: Verify the deployment

```bash
oc get pods -n monitoring
```

Check the services:

```bash
oc get svc -n monitoring
```

Important services include:

- `monitoring-grafana`
- `monitoring-kube-prometheus-prometheus`
- `monitoring-kube-prometheus-alertmanager`
- `monitoring-kube-state-metrics`
- `monitoring-prometheus-node-exporter`

Verify that the required pods are running and ready before proceeding.

## 4. Access Grafana

### Step 1: Expose Grafana through an OpenShift route

```bash
oc expose svc/monitoring-grafana -n monitoring
```

Get the route:

```bash
oc get route -n monitoring
```

Open the displayed Grafana route URL in a browser.

### Step 2: Retrieve the Grafana password

```bash
oc get secret monitoring-grafana -n monitoring \
  -o jsonpath='{.data.admin-password}' | base64 -d
echo
```

Log in using:

- **Username:** `admin`
- **Password:** Retrieved from the Kubernetes Secret

Alternatively, access Grafana locally through port forwarding:

```bash
oc port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Open `http://localhost:3000`.

## 5. Create the Deliver monitoring dashboard

In Grafana, create a new dashboard named **Deliver Namespace Monitoring**.

Add the following four panels. For each panel, select the appropriate visualization, enter the PromQL query, and click **Apply**. Add the remaining panels to the same dashboard and save it.

### Panel 1: CPU usage per pod

**Purpose:** Displays CPU consumption for each pod in the `deliver` namespace.

PromQL query:

```promql
sum by (pod) (
  rate(container_cpu_usage_seconds_total{
    namespace="deliver",
    container!="",
    container!="POD"
  }[5m])
)
```

Recommended settings:
- Visualization: Time series
- Unit: Cores
- Legend: `{{pod}}`

The query calculates the average CPU usage rate over the previous five minutes.

### Panel 2: Memory usage per pod

**Purpose:** Displays the current working memory usage for each pod.

PromQL query:

```promql
sum by (pod) (
  container_memory_working_set_bytes{
    namespace="deliver",
    container!="",
    container!="POD"
  }
)
```

Recommended settings:
- Visualization: Time series
- Unit: Bytes (IEC)
- Legend: `{{pod}}`

This query uses working-set memory, which is useful for tracking the memory actively used by containers.

### Panel 3: Container restart count

**Purpose:** Shows the cumulative number of container restarts for each pod.

PromQL query:

```promql
sum by (pod) (
  kube_pod_container_status_restarts_total{
    namespace="deliver"
  }
)
```

Recommended settings:
- Visualization: Time series or Bar chart
- Legend: `{{pod}}`

For restarts during the previous hour instead of the cumulative count, use:

```promql
sum by (pod) (
  increase(
    kube_pod_container_status_restarts_total{
      namespace="deliver"
    }[1h]
  )
)
```

### Panel 4: Pod readiness

**Purpose:** Shows whether each pod has a ready status.

PromQL query:

```promql
max by (pod) (
  kube_pod_status_ready{
    namespace="deliver",
    condition="true"
  }
)
```

Recommended settings:
- Visualization: State timeline or Stat
- Legend: `{{pod}}`

Interpretation:
- `1` = Pod is ready.
- `0` = Pod is not ready.

To display the total number of ready pods, use:

```promql
sum(
  kube_pod_status_ready{
    namespace="deliver",
    condition="true"
  } == 1
)
```

## 6. Configure the container restart alert

A Grafana alert was created with the following configuration.

| Setting | Value |
|---|---|
| Alert rule name | `Project-Container-Restart` |
| Grafana folder | `project` |
| Namespace | `deliver` |
| Evaluation condition | Query result above `0` |
| Evaluation window | Previous 5 minutes |
| Notification contact point | Not configured |

### PromQL query

```promql
sum by (pod) (
  increase(
    kube_pod_container_status_restarts_total{
      namespace="deliver"
    }[5m]
  )
)
```

### Alert configuration

1. Open **Grafana → Alerting → Alert rules**.
2. Create or edit `Project-Container-Restart`.
3. Configure the PromQL query above.
4. Set the alert condition to trigger when the result is greater than `0`.
5. Configure the evaluation interval, for example, every one minute.
6. Configure the pending period according to the desired response time.
7. Save the alert rule.

The alert evaluates container restart metrics in the `deliver` namespace. If a pod has multiple containers, the query groups restart increases by pod.

**Important:** A pod being deleted and recreated does not necessarily increment the same pod's container restart counter. This alert specifically detects container restart increases within the five-minute query window.


### Step 3: Verify the alert in Grafana

Navigate to **Grafana → Alerting → Alert rules** or **Alert instances**.

The test produced the following alert instance:

- Alert: `Project-Container-Restart`
- Pod: `restart-test`
- Status: `Active`

This confirms that the alert rule detected the restart condition.



## 10. Final outcome

The following monitoring capabilities were configured and tested:

- Prometheus and Grafana deployed through Helm.
- Grafana exposed through an OpenShift route.
- Deliver namespace dashboard with CPU, memory, container restart, and pod readiness panels.
- Container restart alert configured for the `deliver` namespace.
- Temporary test pod used to confirm that the restart alert becomes active.
- External notification delivery identified as a separate configuration step.

**Result:** The Grafana dashboard and container restart alert provide visibility into the health and resource usage of workloads in the `deliver` namespace. External notifications require an additional contact point configuration.
