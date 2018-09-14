import com.santaba.agent.groovyapi.snmp.Snmp;

// Set environment variables.
def hostname = hostProps.get('system.hostname');
def props = hostProps.toProperties()
def snmp_timeout = 10000

def OID_model = "1.3.6.1.2.1.1.1.0" // the OID we want 
def model = Snmp.get(hostname, OID_model);
println "model=${model}" //show on screen 
def OID_uptime = "1.3.6.1.2.1.1.3.0" // the OID we want 
def uptime = Snmp.get(hostname, OID_uptime); 
println "uptime=${uptime}"
def OID_contact = "1.3.6.1.2.1.1.4.0" // the OID we want 
def contact = Snmp.get(hostname, OID_contact); 
println "contact=${contact}"
def OID_system_name = "1.3.6.1.2.1.1.5.0" // the OID we want 
def system_name = Snmp.get(hostname, OID_system_name); 
println "system_name=${system_name}"
def OID_location = "1.3.6.1.2.1.1.6.0" // the OID we want 
def location = Snmp.get(hostname, OID_location); 
println "location=${location}"
return 0