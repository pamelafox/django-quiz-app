targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@secure()
@description('PostGreSQL Server administrator password')
param postgresAdminPassword string

@description('Id of the user or app to assign application roles')
param principalId string = ''

@secure()
@description('Django SECRET_KEY for cryptographic signing')
param djangoSecretKey string

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

var postgresServerName = '${prefix}-postgresql'
var postgresAdminUser = 'admin${uniqueString(resourceGroup.id)}'
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
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    databaseNames: [ postgresDatabaseName ]
    allowAzureIPsFirewall: true
  }
}

module web 'core/host/appservice.bicep' = {
  name: 'appservice'
  scope: resourceGroup
  params: {
    name: '${prefix}-appservice'
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
      DBHOST: '${postgresServerName}.postgres.database.azure.com'
      DBNAME: postgresDatabaseName
      DBUSER: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=postgresAdminUser)'
      DBPASS: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=postgresAdminPassword)'
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
    principalId: principalId
  }
}

var secrets = [
  {
    name: 'djangoSecretKey'
    value: djangoSecretKey
  }
  {
    name: 'postgresAdminUser'
    value: postgresAdminUser
  }
  {
    name: 'postgresAdminPassword'
    value: postgresAdminPassword
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

output WEB_URI string = 'https://${web.outputs.uri}'
output AZURE_LOCATION string = location
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name