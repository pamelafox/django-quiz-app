targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Entra admin role name')
param postgresEntraAdministratorName string

@description('Entra admin role object ID (in Entra)')
param postgresEntraAdministratorObjectId string

@description('Entra admin user type')
@allowed([
  'User'
  'Group'
  'ServicePrincipal'
])
param postgresEntraAdministratorType string = 'User'

@description('Id of the user or app to assign application roles')
param principalId string = ''

@secure()
@description('Django SECRET_KEY for cryptographic signing')
param djangoSecretKey string

@description('Running on GitHub Actions?')
param runningOnGh bool = false

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

var postgresServerName = '${prefix}-postgresql'
var postgresDatabaseName = 'django'

module postgresServer 'core/database/postgresql/flexibleserver.bicep' = {
  name: 'postgresql'
  scope: resourceGroup
  params: {
    name: postgresServerName
    location: location
    tags: tags
    sku: {
      name: 'Standard_B1ms'
      tier: 'Burstable'
    }
    storage: {
      storageSizeGB: 32
    }
    version: '14'
    authType: 'EntraOnly'
    entraAdministratorName: postgresEntraAdministratorName
    entraAdministratorObjectId: postgresEntraAdministratorObjectId
    entraAdministratorType: postgresEntraAdministratorType
    databaseNames: [ postgresDatabaseName ]
    allowAzureIPsFirewall: true
    allowAllIPsFirewall: true // Necessary for post-provision script, can be disabled after
  }
}

var webAppName = '${prefix}-app-service'
module web 'core/host/appservice.bicep' = {
  name: 'appservice'
  scope: resourceGroup
  params: {
    name: webAppName
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.11'
    scmDoBuildDuringDeployment: true
    ftpsState: 'Disabled'
    managedIdentity: true
    appCommandLine: 'python manage.py migrate && gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile \'-\' --error-logfile \'-\' --bind=0.0.0.0:8000 --chdir=/home/site/wwwroot quizsite.wsgi'
    appSettings: {
      ADMIN_URL: 'admin${uniqueString(appServicePlan.outputs.id)}'
      DBENGINE: 'django.db.backends.postgresql'
      DBHOST: postgresServer.outputs.POSTGRES_DOMAIN_NAME
      DBNAME: postgresDatabaseName
      DBUSER: webAppName
      DBSSL: 'require'
      STATIC_BACKEND: 'whitenoise.storage.CompressedManifestStaticFilesStorage'
      SECRET_KEY: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=djangoSecretKey)'
    }
  }
}

module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'serviceplan'
  scope: resourceGroup
  params: {
    name: '${prefix}-serviceplan'
    location: location
    tags: tags
    sku: {
      name: 'B1'
    }
    reserved: true
  }
}

module webKeyVaultAccess 'core/security/keyvault-access.bicep' = {
  name: 'web-keyvault-access'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    principalId: web.outputs.identityPrincipalId
  }
}

// Store secrets in a keyvault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}-vault'
    location: location
    tags: tags
  }
}

module userKeyVaultAccess 'core/security/role.bicep' = {
  name: 'user-keyvault-access'
  scope: resourceGroup
  params: {
    principalId: principalId
    principalType: runningOnGh ? 'ServicePrincipal' : 'User'
    roleDefinitionId: '00482a5a-887f-4fb3-b363-3b7fe8e74483'
  }
}

module backendKeyVaultAccess 'core/security/role.bicep' = {
  name: 'backend-keyvault-access'
  scope: resourceGroup
  params: {
    principalId: web.outputs.identityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: '00482a5a-887f-4fb3-b363-3b7fe8e74483'
  }
}

var secrets = [
  {
    name: 'djangoSecretKey'
    value: djangoSecretKey
  }
]

@batchSize(1)
module keyVaultSecrets './core/security/keyvault-secret.bicep' = [for secret in secrets: {
  name: 'keyvault-secret-${secret.name}'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    name: secret.name
    secretValue: secret.value
  }
}]



module logAnalyticsWorkspace 'core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  scope: resourceGroup
  params: {
    name: '${prefix}-loganalytics'
    location: location
    tags: tags
  }
}

output WEB_APP_NAME string = webAppName
output WEB_URI string = 'https://${web.outputs.uri}'
output SERVICE_WEB_IDENTITY_NAME string = webAppName

output AZURE_LOCATION string = location
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name

output POSTGRES_HOST string = postgresServer.outputs.POSTGRES_DOMAIN_NAME
output POSTGRES_USERNAME string = postgresEntraAdministratorName
