function initMap() {

	var rbd = {
		info: '<strong>Ralph Brown Draughon Library</strong><br>231 Mell St<br>Auburn, AL 36849<br><a href="https://www.google.com/maps/place/231+Mell+St,+Auburn,+AL+36849/@32.6029548,-85.4849207,17z/data=!3m1!4b1!4m5!3m4!1s0x888cf3034a1ce893:0xabaf3db7e9ed3f25!8m2!3d32.6029548!4d-85.4827267">Get Directions</a>',
		lat: 32.603025,
		long: -85.4828133
	};

	var greene = {
		info: '<strong>Greene Hall, College of Veterinary Medicine</strong><br>1130 Wire Road<br>Auburn, AL 36832<br><a href="https://www.google.com/maps/place/1130+Wire+Rd,+Auburn,+AL+36832/data=!4m2!3m1!1s0x888cf382dbed6e1d:0x6d8f926e25989339?ved=2ahUKEwjNpJnz25_gAhVudt8KHZr0AJIQ8gEwAHoECAAQAQ">Get Directions</a>',
		lat: 32.599305,
		long: -85.4971808
	};

	var hunters = {
		info: '<strong>Hunter\'s First Floor Shelter</strong><br>211 W Longleaf Drive<br>Auburn, AL 36832<br><a href="https://www.google.com/maps/place/211+W+Longleaf+Dr,+Auburn,+AL+36832/@32.5725727,-85.5050344,17z/data=!3m1!4b1!4m5!3m4!1s0x888cf394f6b651b9:0xf9403c470fa4c622!8m2!3d32.5725727!4d-85.5028404">Get Directions</a>',
		lat: 32.572604,
		long: -85.502795
	};

	var locations = [
      [rbd.info, rbd.lat, rbd.long, 0],
      [greene.info, greene.lat, greene.long, 1],
      [hunters.info, hunters.lat, hunters.long, 2],
    ];

	var map = new google.maps.Map(document.getElementById('map'), {
		zoom: 13,
		center: new google.maps.LatLng(32.590, -85.4900),
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});

	var infowindow = new google.maps.InfoWindow({});

	var marker, i;

	for (i = 0; i < locations.length; i++) {
		marker = new google.maps.Marker({
			position: new google.maps.LatLng(locations[i][1], locations[i][2]),
			map: map
		});

		google.maps.event.addListener(marker, 'click', (function (marker, i) {
			return function () {
				infowindow.setContent(locations[i][0]);
				infowindow.open(map, marker);
			}
		})(marker, i));
	}
}