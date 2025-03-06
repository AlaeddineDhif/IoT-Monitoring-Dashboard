<?php

$hostname = "localhost"; 
$username = "root"; 
$password = ""; 
$database = "sensor_db"; 

$conn = mysqli_connect($hostname, $username, $password, $database);


if (!$conn) { 
	die("Connection failed: " . mysqli_connect_error()); 
} 

echo "Database connection is OK<br>"; 
if(isset($_POST ["temperature"]) && isset($_POST["humidity"])) {
	

    $t = floatval($_POST["temperature"]); // Convertir la chaîne en float
    $h = floatval($_POST["humidity"]);    // Convertir la chaîne en float



	$sql = "INSERT INTO dht22 ( Temperature , Humidity ) VALUES (".$t.",".$h.")";

	if (mysqli_query($conn , $sql)) {
		echo "NEW Record Created Succesfully" ;
	} else {
		echo "Erur :".$sql. "<br>" .mysqli_error($conn);
	}
}



?>