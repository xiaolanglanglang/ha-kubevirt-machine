# Home Assistant Kubevirt Manager

这是一个用于管理 Kubevirt 虚拟机的 Home Assistant 集成。

## 功能

- 查看虚拟机的状态
- 支持虚拟机的开启、关闭、重启等操作

## 安装

1. 在 HACS 中搜索并安装 "Home Assistant Kubevirt Machine"
2. 重启 Home Assistant

## 配置说明

此集成需要在 Kubernetes 集群中创建一个具有适当权限的 ServiceAccount 来管理 Kubevirt 虚拟机。以下是配置步骤的概述：

1. 创建一个 ServiceAccount, 此处命名为 `ha-kubevirt-user`, 并将其命名空间设置为 `default`。

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ha-kubevirt-user
  namespace: default
```

2. 创建一个 Role，定义对操作 Kubevirt 虚拟机的必要权限，此处命名为 `ha-kubevirt-user-role`，并将其命名空间设置为 `default`。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: ha-kubevirt-user-role
rules:
  - apiGroups:
      - kubevirt.io
    resources:
      - virtualmachines
      - virtualmachineinstances
    verbs:
      - get
      - list
      - watch
      - update
  - apiGroups:
      - subresources.kubevirt.io
    resources:
      - virtualmachines/start
      - virtualmachines/stop
    verbs:
      - update
```

3. 创建一个 RoleBinding，将 ServiceAccount 与 Role 绑定，此处命名为 `ha-kubevirt-user-binding`，并将其命名空间设置为 `default`。

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ha-kubevirt-user-binding
  namespace: default
subjects:
  - kind: ServiceAccount
    name: ha-kubevirt-user
    namespace: default
roleRef:
  kind: Role
  name: ha-kubevirt-user-role
  apiGroup: rbac.authorization.k8s.io
```

4. 创建一个 Secret，用于生成访问令牌，此处命名为 `ha-kubevirt-user`，并将其命名空间设置为 `default`。

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ha-kubevirt-user
  namespace: default
  annotations:
    kubernetes.io/service-account.name: "ha-kubevirt-user"
type: kubernetes.io/service-account-token
```

5. 在 Home Assistant 中添加集成，使用上述 Secret 的令牌中的信息进行验证。

```
api_url: <Kubevirt API 的 URL>
api_token: <Kubevirt API 的令牌>
api_ca_cert: <Kubevirt API 的 CA 证书>
namespace: <Kubevirt 的命名空间>
```
