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
param databasePassword string

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'

var postgresServerName = '${prefix}-postgresql'

module virtualNetwork 'core/security/virtualnetwork.bicep' = {
  name: 'virtualnetwork'
  scope: resourceGroup
  params: {
    name: '${prefix}-vnet'
    location: location
    tags: tags
    postgresServerName: postgresServerName
  }
}

var databaseName = 'django'
var databaseUser = 'django'

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
    version: '13'
    administratorLogin: databaseUser
    administratorLoginPassword: databasePassword
    databaseName: databaseName
    delegatedSubnetResourceId: virtualNetwork.outputs.databaseSubnetId
    privateDnsZoneArmResourceId: virtualNetwork.outputs.privateDnsZoneId
    privateDnsZoneLink: virtualNetwork.outputs.privateDnsZoneLink
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
    runtimeVersion: '3.10'
    scmDoBuildDuringDeployment: true
    ftpsState: 'Disabled'
    managedIdentity: true
    appCommandLine: 'python manage.py migrate && gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile \'-\' --error-logfile \'-\' --bind=0.0.0.0:8000 --chdir=/home/site/wwwroot quizsite.wsgi'
    virtualNetwork: virtualNetwork
    subnetResourceId: virtualNetwork.outputs.webSubnetId
    appSettings: {
      DBHOST: postgresServerName
      DBNAME: databaseName
      DBUSER: databaseUser
      DBPASS: databasePassword
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
